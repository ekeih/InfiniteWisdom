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
import os
from infinitewisdom.analysis import ImageAnalyser


class GoogleVision(ImageAnalyser):
    """
    Google Vision API implementation
    """

    def __init__(self, auth_file_path: str):
        """
        :param auth_file_path: authentication file for the google vision api
        """
        # Imports the Google Cloud client library
        from google.cloud import vision

        self._auth_file_path = auth_file_path
        self._auth_id = os.path.split(auth_file_path)[1]

        # Instantiates a client
        self._client = vision.ImageAnnotatorClient.from_service_account_file(auth_file_path)

    def get_identifier(self) -> str:
        from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_GOOGLE_VISION
        return IMAGE_ANALYSIS_TYPE_GOOGLE_VISION

    def get_quality(self) -> float:
        return 0.9

    def get_monthly_capacity(self) -> float:
        return 1000.0

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
