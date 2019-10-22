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
import os

from container_app_conf import ConfigBase
from container_app_conf.entry.bool import BoolConfigEntry
from container_app_conf.entry.float import FloatConfigEntry
from container_app_conf.entry.int import IntConfigEntry
from container_app_conf.entry.list import ListConfigEntry
from container_app_conf.entry.string import StringConfigEntry

from infinitewisdom.const import CONFIG_FILE_NAME, \
    CONFIG_NODE_ROOT, \
    CONFIG_NODE_IMAGE_ANALYSIS, CONFIG_NODE_PERSISTENCE, DEFAULT_SQL_PERSISTENCE_URL, \
    CONFIG_NODE_CRAWLER, CONFIG_NODE_TELEGRAM, CONFIG_NODE_GOOGLE_VISION, \
    CONFIG_NODE_TESSERACT, CONFIG_NODE_ENABLED, CONFIG_NODE_CAPACITY_PER_MONTH, CONFIG_NODE_INTERVAL, \
    CONFIG_NODE_UPLOADER, DEFAULT_FILE_PERSISTENCE_BASE_PATH, CONFIG_NODE_MICROSOFT_AZURE, CONFIG_NODE_PORT, \
    CONFIG_NODE_STATS


class AppConfig(ConfigBase):
    """
    Main InfiniteWisdom bot configuration
    """

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)

    @property
    def config_file_names(self) -> [str]:
        return [CONFIG_FILE_NAME]

    TELEGRAM_BOT_TOKEN = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "bot_token"
        ],
        example="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        secret=True)

    TELEGRAM_INLINE_BADGE_SIZE = IntConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "inline_badge_size"
        ],
        default=16)

    TELEGRAM_GREETING_MESSAGE = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "greeting_message"
        ],
        required=False,
        default='Send /inspire for more inspiration :blush: Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.')

    TELEGRAM_CAPTION_IMAGES_WITH_TEXT = BoolConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "caption_images_with_text"
        ],
        default=False)

    TELEGRAM_ADMIN_USERNAMES = ListConfigEntry(
        item_type=StringConfigEntry,
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "admin_usernames"
        ],
        default=[],
        example=[
            "myadminuser",
            "myotheradminuser"
        ]
    )

    UPLOADER_INTERVAL = FloatConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_UPLOADER,
            CONFIG_NODE_INTERVAL
        ],
        default=3.0)

    UPLOADER_CHAT_ID = IntConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_UPLOADER,
            "chat_id"
        ],
        default=None,
        example=12345678)

    CRAWLER_INTERVAL = FloatConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_CRAWLER,
            CONFIG_NODE_INTERVAL
        ],
        default=1.0)

    SQL_PERSISTENCE_URL = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "url"
        ],
        default=DEFAULT_SQL_PERSISTENCE_URL,
        secret=True)

    FILE_PERSISTENCE_BASE_PATH = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "file_base_path"
        ],
        default=DEFAULT_FILE_PERSISTENCE_BASE_PATH)

    IMAGE_ANALYSIS_INTERVAL = FloatConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_INTERVAL
        ],
        default=1.0)

    IMAGE_ANALYSIS_TESSERACT_ENABLED = BoolConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_TESSERACT,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED = BoolConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            "auth_file"
        ],
        default=None,
        example="./InfiniteWisdom-1522618e7d39.json")

    IMAGE_ANALYSIS_GOOGLE_VISION_CAPACITY = IntConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            CONFIG_NODE_CAPACITY_PER_MONTH
        ],
        default=None,
        example=1000)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_ENABLED = BoolConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_SUBSCRIPTION_KEY = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            "subscription_key"
        ],
        default=None,
        example="1234567890684c3baa5a0605712345ab",
        secret=True)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_REGION = StringConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            "region"
        ],
        default="francecentral")

    IMAGE_ANALYSIS_MICROSOFT_AZURE_CAPACITY = IntConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            CONFIG_NODE_CAPACITY_PER_MONTH
        ],
        default=5000)

    STATS_PORT = IntConfigEntry(
        key_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_STATS,
            CONFIG_NODE_PORT
        ],
        default=8000
    )

    def _validate(self):
        """
        Validates the current configuration and throws an exception if something is wrong
        """
        if len(self.TELEGRAM_BOT_TOKEN.value) <= 0:
            raise AssertionError("Bot token is missing!")
        if self.CRAWLER_INTERVAL.value < 0:
            raise AssertionError("Image polling interval must be >= 0!")

        if self.IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED.value:
            if self.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value is None:
                raise AssertionError("Google Vision authentication file is required")

            if not os.path.isfile(
                    self.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value):
                raise IsADirectoryError("Google Vision Auth file path is not a file: {}".format(
                    self.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value))

        if self.IMAGE_ANALYSIS_MICROSOFT_AZURE_ENABLED.value:
            if self.IMAGE_ANALYSIS_MICROSOFT_AZURE_SUBSCRIPTION_KEY.value is None:
                raise AssertionError("Microsoft Azure subscription key is required")

            if self.IMAGE_ANALYSIS_MICROSOFT_AZURE_REGION.value is None:
                raise AssertionError("Microsoft Azure region is required")
