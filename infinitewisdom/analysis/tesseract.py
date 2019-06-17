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
import math
import sys

from infinitewisdom.analysis import ImageAnalyser

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Tesseract(ImageAnalyser):
    """
    pytesseract implementation
    """

    def get_identifier(self) -> str:
        from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_TESSERACT
        return IMAGE_ANALYSIS_TYPE_TESSERACT

    def get_quality(self) -> float:
        return 0.25

    def get_monthly_capacity(self):
        return math.inf

    def find_text(self, image: bytes):
        try:
            from PIL import Image
        except ImportError:
            import Image
        import pytesseract

        # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
        try:
            image = self._preprocess(image)

            # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
            text = pytesseract.image_to_string(image)
            return text
        except:
            ex = sys.exc_info()[0]
            LOGGER.error(ex)
            return None

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
