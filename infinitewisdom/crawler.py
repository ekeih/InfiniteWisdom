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
import time

import requests

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence, Entity

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Crawler:
    """
    Crawler used to fetch new images from the image API
    """

    def __init__(self, config: Config, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
        """
        Creates a crawler instance.
        :param persistence: crawled data is added here
        """
        self._config = config
        self._persistence = persistence
        self._image_analysers = image_analysers

        self._timer = None

    def start(self):
        """
        Starts crawling
        """
        self._schedule_next_run()

    def stop(self):
        """
        Stops crawling
        """
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None

    def _schedule_next_run(self):
        """
        Schedules the next run
        """
        self._timer = threading.Timer(self._config.CRAWLER_TIMEOUT.value, self._crawl_job)
        self._timer.start()

    def _crawl_job(self):
        """
        The job that is executed regularly by this crawler
        """
        try:
            self._add_image_url_to_pool()
        except Exception as e:
            LOGGER.error(e)
        finally:
            self._schedule_next_run()

    def _add_image_url_to_pool(self) -> str or None:
        """
        Requests a new image url and adds it to the pool
        :return: the added url
        """
        url = self._fetch_generated_image_url()

        if len(self._persistence.find_by_url(url)) > 0:
            LOGGER.debug("Entity with url '{}' already in persistence, skipping.".format(url))
            return None

        entity = Entity(url, None, None, None, time.time(), None)
        self._persistence.add(entity)
        LOGGER.debug('Added image #{} with URL: "{}"'.format(self._persistence.count(), url))

        return url

    @staticmethod
    def _fetch_generated_image_url() -> str:
        """
        Requests the image api to generate a new image url
        :return: the image url
        """
        url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'})
        url_page.raise_for_status()
        return url_page.text
