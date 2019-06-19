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

import requests

from infinitewisdom import RegularIntervalWorker
from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence, Entity
from infinitewisdom.util import download_image_bytes, create_hash

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Crawler(RegularIntervalWorker):
    """
    Crawler used to fetch new images from the image API
    """

    def __init__(self, config: Config, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
        """
        Creates a crawler instance.
        :param persistence: crawled data is added here
        """
        super().__init__(config.CRAWLER_INTERVAL.value)
        self._persistence = persistence
        self._image_analysers = image_analysers

    def _run(self):
        self._add_image_url_to_pool()

    def _add_image_url_to_pool(self) -> str or None:
        """
        Requests a new image url and adds it to the pool
        :return: the added url
        """
        url = self._fetch_generated_image_url()
        image_data = download_image_bytes(url)
        image_hash = create_hash(image_data)

        existing = self._persistence.find_by_image_hash(image_hash)
        if existing is not None:
            if existing.url != url:
                LOGGER.warning(
                    'Found already known image hash for a different url than expected. Old: {} New: {} Hash: {}'.format(
                        existing.url, url, image_hash))
                existing.url = url
            self._persistence.update(existing, image_data)
            return None

        entity = Entity(url=url, created=time.time())
        self._persistence.add(entity, image_data)
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
