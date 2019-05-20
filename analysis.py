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


class Tesseract(ImageAnalyser):
    """
    pytesseract implementation
    """

    def find_text(self, image: bytes):
        try:
            from PIL import Image
        except ImportError:
            import Image
        import pytesseract

        # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'

        image = self._preprocess(image)

        # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
        text = pytesseract.image_to_string(image)
        return text

    @staticmethod
    def _preprocess(image: bytes) -> bytes:
        """
        Applies pre-processing to a given image to improve text recognition
        :param image: the original image to process
        :return: the processed image
        """
        import cv2
        import numpy as np

        bytes_as_np_array = np.frombuffer(image, dtype=np.uint8)
        flags = cv2.IMREAD_GRAYSCALE
        image = cv2.imdecode(bytes_as_np_array, flags)

        # apply slight blur
        image = cv2.medianBlur(image, 3)

        return image
