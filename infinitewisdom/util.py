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

import requests

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def download_image_bytes(url: str) -> bytes:
    """
    Downloads the image from the given url
    :return: the downloaded image
    """
    image = requests.get(url)
    image.raise_for_status()
    LOGGER.debug('Fetched image from: {}'.format(url))
    return image.content
