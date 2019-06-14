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


class ImageAnalyser:
    """
    Base class for image analysis
    """

    def get_identifier(self) -> str:
        """
        :return: an identifier for this analyser
        """
        raise NotImplementedError()

    def get_quality(self) -> float:
        """
        :return: the quality of this analyser compared to other implementations
        """
        raise NotImplementedError()

    def get_monthly_capacity(self) -> float:
        """
        :return: the number of items per month that can be analysed by this analyser
        """
        raise NotImplementedError()

    def find_text(self, image: bytes) -> str or None:
        """
        Analyses the given image
        :param image: the image to analyse
        :return: recognized text
        """
        raise NotImplementedError()
