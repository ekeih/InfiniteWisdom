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

import requests

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.stats import MICROSOFT_AZURE_FIND_TEXT_TIME


class AzureComputerVision(ImageAnalyser):
    """
    Microsoft Azure Computer Vision API implementation
    """

    def __init__(self, subscription_key: str, region: str = "francecentral", monthly_capacity: float = None):
        """
        :param subscription_key: subscription key
        :param region: You must use the same region in your REST call as you used to get your subscription keys.
        :param monthly_capacity: custom monthly capacity (optional)
        """
        self._subscription_key = subscription_key
        self._region = region

        vision_base_url = "https://{}.api.cognitive.microsoft.com/vision/v2.0/".format(self._region)
        self._ocr_url = vision_base_url + "ocr"

        if monthly_capacity is None:
            self._monthly_capacity = 1000.0
        else:
            self._monthly_capacity = float(monthly_capacity)

    def get_identifier(self) -> str:
        from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_AZURE
        return IMAGE_ANALYSIS_TYPE_AZURE

    def get_quality(self) -> float:
        return 0.85

    def get_monthly_capacity(self) -> float:
        return self._monthly_capacity

    @MICROSOFT_AZURE_FIND_TEXT_TIME.time()
    def find_text(self, image: bytes):
        headers = {
            'Content-Type': 'application/octet-stream',  # this is necessary for binary image data upload
            'Ocp-Apim-Subscription-Key': self._subscription_key
        }
        # language is set to "en" for improved results, use "unk" if the language is unknown
        # we also don't need orientation because we know all text is normally oriented
        params = {
            'language': 'en',
            'detectOrientation': 'false'
        }

        # a url can also be used
        # json_data = {'url': image_url}
        # response = requests.post(self._ocr_url, headers=headers, params=params, json=json_data)

        response = requests.post(self._ocr_url, headers=headers, params=params, data=image)
        response.raise_for_status()
        analysis = response.json()

        # Extract the word bounding boxes and text.
        line_infos = [region["lines"] for region in analysis["regions"]]
        word_infos = []
        for line in line_infos:
            for word_metadata in line:
                for word_info in word_metadata["words"]:
                    word_infos.append(word_info)
        text = ' '.join(filter(lambda x: x is not None, map(lambda x: x.get('text', None), word_infos)))

        if len(text) > 0:
            return text
        else:
            return None
