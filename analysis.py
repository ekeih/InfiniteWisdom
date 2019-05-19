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

    def find_text(self, image: bytes) -> str or None:
        """
        Analyses the given image
        :param image: the image to analyse
        :return: recognized text
        """
        raise NotImplementedError()


class GoogleVision(ImageAnalyser):
    """
    Google Vision API implementation
    """

    def __init__(self, auth_file: str):
        """
        :param auth_file: authentication file for the google vision api
        """
        # Imports the Google Cloud client library
        from google.cloud import vision

        # Instantiates a client
        self._client = vision.ImageAnnotatorClient.from_service_account_file(auth_file)

    def find_text(self, image: bytes):
        from google.cloud.vision import types

        image = types.Image(content=image)

        # Performs label detection on the image file
        response = self._client.text_detection(image=image)
        text_annotations = response.text_annotations
        # the first annotation contains the whole thing
        if len(text_annotations) > 0:
            return text_annotations[0].description
        else:
            return None
