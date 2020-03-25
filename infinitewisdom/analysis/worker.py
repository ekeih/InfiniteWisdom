# InfiniteWisdomBot - A Telegram bot that sends inspirational quotes of infinite wisdom...
# Copyright (C) 2019  Max Rosin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging
import time

from infinitewisdom import RegularIntervalWorker
from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config.config import AppConfig
from infinitewisdom.persistence import ImageDataPersistence, _session_scope
from infinitewisdom.stats import ANALYSER_TIME, ANALYSER_CAPACITY
from infinitewisdom.util import select_best_available_analyser, format_for_single_line_log, remaining_capacity, \
    download_image_bytes

LOGGER = logging.getLogger(__name__)


class AnalysisWorker(RegularIntervalWorker):
    """
    Worker that continuously scans the persistence and tries to add or upgrade their analysis.
    """

    def __init__(self, config: AppConfig, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
        """
        Creates an instance
        :param config: the configuration
        :param persistence: the persistence
        :param image_analysers: available image analysers
        """
        super().__init__(config.IMAGE_ANALYSIS_INTERVAL.value)
        self._config = config
        self._persistence = persistence
        self._image_analysers = image_analysers

        if len(self._image_analysers) <= 0:
            LOGGER.warning("No image analyser provided")
            self._target_quality = 0
        else:
            self._target_quality = sorted(self._image_analysers, key=lambda x: x.get_quality(), reverse=True)[
                0].get_quality()

        with _session_scope() as session:
            self._not_optimal_ids = set(self._persistence.find_non_optimal(session, self._target_quality))

    def start(self):
        if len(self._image_analysers) <= 0:
            LOGGER.warning("No image analyser provided, not starting.")
            return

        with _session_scope(False) as session:
            self._update_stats(session)

        super().start()

    def add_image_to_queue(self, image_entity_id: int):
        self._not_optimal_ids.add(image_entity_id)

    @ANALYSER_TIME.time()
    def _run(self):
        """
        The job that is executed regularly by this crawler
        """
        with _session_scope() as session:
            if len(self._not_optimal_ids) <= 0:
                # sleep for a longer time period to reduce load
                time.sleep(60)
                self._not_optimal_ids = set(self._persistence.find_non_optimal(session, self._target_quality))
                return

            entity = None
            while entity is None:
                if len(self._not_optimal_ids) <= 0:
                    return
                image_id = self._not_optimal_ids.pop()
                entity = self._persistence.get_image(session, image_id)
                if entity is None:
                    LOGGER.warning(f"Image id scheduled for analysis not found: {image_id}")
                    # the entity has probably been removed in the meantime
                    continue

            analyser = select_best_available_analyser(session, self._image_analysers, self._persistence)
            if analyser is None:
                # No analyser available, skipping
                # sleep for a longer time period to reduce db load
                time.sleep(60)
                return

            if entity.analyser_quality is not None and entity.analyser_quality >= analyser.get_quality():
                LOGGER.debug(
                    "Not analysing '{}' with '{}' because it wouldn't improve analysis quality ({} vs {})".format(
                        entity.url, analyser.get_identifier(), entity.analyser_quality, analyser.get_quality()))
                # sleep for a longer time period to reduce db load
                time.sleep(60)
                return

            image_data = self._persistence.get_image_data(entity)
            if image_data is None:
                LOGGER.warning(
                    "No image data found for entity with image_hash {}, it will not be analysed.".format(
                        entity.image_hash))
                try:
                    image_data = download_image_bytes(entity.url)
                    self._persistence.update(session, entity, image_data)
                except Exception as e:
                    # if len(entity.telegram_ids) > 0:
                    #     LOGGER.warning(
                    #         "Error downloading image data from original source, using telegram upload instead. {}".format(
                    #             entity))
                    #     # TODO:
                    # else:
                    LOGGER.error(
                        "Error trying to download missing image data for url '{}', deleting entity.".format(entity.url),
                        e)
                    self._persistence.delete(session, entity)
                return

            old_analyser = entity.analyser
            old_quality = entity.analyser_quality
            if old_quality is None:
                old_quality = 0

            entity.analyser = analyser.get_identifier()
            entity.analyser_quality = analyser.get_quality()
            new_text = analyser.find_text(image_data)

            if (new_text is None or len(new_text) <= 0) and entity.text is not None and len(entity.text) > 0:
                LOGGER.debug("Ignoring new analysis text because it would delete it")
            else:
                entity.text = new_text

            self._persistence.update(session, entity, image_data)
            LOGGER.debug(
                "Updated analysis of '{}' with '{}' (was '{}') with a quality improvement of {} ({} -> {}): {}".format(
                    entity.url, analyser.get_identifier(), old_analyser, entity.analyser_quality - old_quality,
                    old_quality,
                    entity.analyser_quality,
                    format_for_single_line_log(entity.text)))

            self._update_stats(session)

    def _update_stats(self, session):
        for analyser in self._image_analysers:
            remaining = remaining_capacity(session, analyser, self._persistence)
            ANALYSER_CAPACITY.labels(name=analyser.get_identifier()).set(remaining)
