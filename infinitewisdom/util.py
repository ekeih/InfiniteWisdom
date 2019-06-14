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

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.persistence import ImageDataPersistence

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


def select_best_available_analyser(analysers: [ImageAnalyser],
                                   persistence: ImageDataPersistence) -> ImageAnalyser or None:
    """
    Selects the best available analyser based on it's quality and remaining capacity
    :param analysers: the analysers to choose from
    :param persistence: currently in use persistence
    :return: analyser or None
    """

    if len(analysers) == 1:
        return analysers[0]

    def remaining_capacity(analyser) -> int:
        """
        Calculates the remaining capacity of an analyser
        :param analyser: the analyser to check
        :return: the remaining capacity of the analyser
        """
        count = persistence.count_items_this_month(analyser.get_identifier())
        remaining = analyser.get_monthly_capacity() - count
        return remaining

    available = filter(lambda x: remaining_capacity(x) > 0, analysers)
    # TODO: this list might be empty!
    optimal = sorted(available, key=lambda x: (-x.get_quality(), -remaining_capacity(x)))[0]
    return optimal
