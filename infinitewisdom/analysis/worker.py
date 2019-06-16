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
import threading

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.util import select_best_available_analyser, download_image_bytes

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class AnalysisWorker:
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
        self._config = config
        self._persistence = persistence
        self._image_analysers = image_analysers

        self._timer = None

        if len(self._image_analysers) <= 0:
            LOGGER.warning("No image analyser provided")
            self._target_quality = 0
        else:
            self._target_quality = sorted(self._image_analysers, key=lambda x: x.get_quality())[0].get_quality()

    def start(self):
        """
        Starts the worker
        """
        if len(self._image_analysers) <= 0:
            LOGGER.warning("No image analyser provided, not starting.")
            return

        self._schedule_next_run()

    def stop(self):
        """
        Stops the worker
        """
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None

    def _schedule_next_run(self):
        """
        Schedules the next run
        """
        self._timer = threading.Timer(self._config.IMAGE_ANALYSIS_INTERVAL.value, self._worker_job)
        self._timer.start()

    def _worker_job(self):
        """
        The job that is executed regularly by this crawler
        """
        try:
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

            if entity.image_data is None:
                image = download_image_bytes(entity.url)
            else:
                image = entity.image_data

            old_analyser = entity.analyser
            old_quality = entity.analyser_quality
            if old_quality is None:
                old_quality = 0

            entity.analyser = analyser.get_identifier()
            entity.analyser_quality = analyser.get_quality()
            entity.text = analyser.find_text(image)

            self._persistence.update(entity)
            LOGGER.debug(
                "Updated analysis of '{}' with '{}' (was '{}') with a quality improvement of {} ({} -> {})".format(
                    entity.url, analyser.get_identifier(), old_analyser, entity.analyser_quality - old_quality,
                    old_quality,
                    entity.analyser_quality))

        except Exception as e:
            LOGGER.error(e)
        finally:
            self._schedule_next_run()
