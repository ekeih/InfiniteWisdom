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

from infinitewisdom import RegularIntervalWorker
from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.util import select_best_available_analyser

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AnalysisWorker(RegularIntervalWorker):
    """
    Worker that continuously scans the persistence and tries to add or upgrade their analysis.
    """

    def __init__(self, config: Config, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
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

    def start(self):
        if len(self._image_analysers) <= 0:
            LOGGER.warning("No image analyser provided, not starting.")
            return

        super().start()

    def _run(self):
        """
        The job that is executed regularly by this crawler
        """
        entity = self._persistence.find_non_optimal(self._target_quality)
        if entity is None:
            # nothing to analyse
            return

        analyser = select_best_available_analyser(self._image_analysers, self._persistence)
        if analyser is None:
            LOGGER.debug("No analyser available, skipping '{}'".format(entity.url))
            return

        if entity.analyser_quality is not None and entity.analyser_quality >= analyser.get_quality():
            LOGGER.debug(
                "Not analysing '{}' with '{}' because it wouldn't improve analysis quality ({} vs {})".format(
                    entity.url, analyser.get_identifier(), entity.analyser_quality, analyser.get_quality()))
            return

        image_data = self._persistence.get_image_data(entity)
        if image_data is None:
            LOGGER.debug(
                "No image data found for entity with image_hash {}, it will not be analysed.".format(entity.image_hash))
            return

        old_analyser = entity.analyser
        old_quality = entity.analyser_quality
        if old_quality is None:
            old_quality = 0

        entity.analyser = analyser.get_identifier()
        entity.analyser_quality = analyser.get_quality()
        entity.text = analyser.find_text(image_data)

        self._persistence.update(entity, image_data)
        LOGGER.debug(
            "Updated analysis of '{}' with '{}' (was '{}') with a quality improvement of {} ({} -> {}): {}".format(
                entity.url, analyser.get_identifier(), old_analyser, entity.analyser_quality - old_quality,
                old_quality,
                entity.analyser_quality, entity.text))
