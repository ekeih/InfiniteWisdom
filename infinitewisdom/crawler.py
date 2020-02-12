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
from infinitewisdom.config.config import AppConfig
from infinitewisdom.const import REQUESTS_TIMEOUT
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.persistence.sqlalchemy import Image, _session_scope
from infinitewisdom.stats import CRAWLER_TIME
from infinitewisdom.util import download_image_bytes, create_hash

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Crawler(RegularIntervalWorker):
    """
    Crawler used to fetch new images from the image API
    """
    URL_CACHE = {}

    def __init__(self, config: AppConfig, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
        """
        Creates a crawler instance.
        :param persistence: crawled data is added here
        """
        super().__init__(config.CRAWLER_INTERVAL.value)
        self._persistence = persistence
        self._image_analysers = image_analysers

    @CRAWLER_TIME.time()
    def _run(self):
        with _session_scope() as session:
            self._add_image_url_to_pool(session)

    def _add_image_url_to_pool(self, session) -> str or None:
        """
        Requests a new image url and adds it to the pool
        :return: the added url
        """
        url = self._fetch_generated_image_url()
        if url in self.URL_CACHE:
            # skip already processed url
            return None

        image_data = download_image_bytes(url)
        image_hash = create_hash(image_data)

        existing = self._persistence.find_by_image_hash(session, image_hash)
        if existing is not None:
            if existing.url != url:
                LOGGER.warning(
                    'Found already known image hash for a different url than expected. Old: {} New: {} Hash: {}'.format(
                        existing.url, url, image_hash))
                existing.url = url
                self._persistence.update(session, existing, image_data)
            self.URL_CACHE[url] = True
            return None

        entity = Image(url=url, created=time.time())
        self._persistence.add(session, entity, image_data)
        LOGGER.debug('Added image #{} with URL: "{}"'.format(self._persistence.count(session), url))

        self.URL_CACHE[url] = True
        return url

    @staticmethod
    def _fetch_generated_image_url() -> str:
        """
        Requests the image api to generate a new image url
        :return: the image url
        """
        url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'}, timeout=REQUESTS_TIMEOUT)
        url_page.raise_for_status()
        return url_page.text
