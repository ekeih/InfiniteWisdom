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

import requests

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.util import download_image_bytes

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
        self._timer = threading.Timer(1.0, self._crawl_job)
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

        analyser_id = None
        analyser_quality = None
        text = None
        if len(self._image_analysers) > 0:
            image = download_image_bytes(url)
            analyser = self._select_analyser()
            analyser_id = analyser.get_identifier()
            analyser_quality = analyser.get_quality()

            text = analyser.find_text(image)

        self._persistence.add(url, None, text, analyser_id, analyser_quality)
        LOGGER.debug(
            'Added image #{} with URL: "{}", analyser: "{}", text:"{}"'.format(self._persistence.count(), url,
                                                                               analyser_id,
                                                                               text))

        return url

    def _select_analyser(self):
        """
        Selects an analyser based on it's quality and remaining capacity
        """

        if len(self._image_analysers) == 1:
            return self._image_analysers[0]

        def remaining_capacity(analyser) -> int:
            """
            Calculates the remaining capacity of an analyser
            :param analyser: the analyser to check
            :return: the remaining capacity of the analyser
            """
            count = self._persistence.count_items_this_month(analyser.get_identifier())
            remaining = analyser.get_monthly_capacity() - count
            return remaining

        available = filter(lambda x: remaining_capacity(x) > 0, self._image_analysers)
        optimal = sorted(available, key=lambda x: (-x.get_quality(), -remaining_capacity(x)))[0]
        return optimal

    @staticmethod
    def _fetch_generated_image_url() -> str:
        """
        Requests the image api to generate a new image url
        :return: the image url
        """
        url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'})
        url_page.raise_for_status()
        return url_page.text
