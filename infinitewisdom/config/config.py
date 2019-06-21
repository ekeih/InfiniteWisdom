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

import yaml

from infinitewisdom.config import StringConfigEntry, IntConfigEntry, FloatConfigEntry, BoolConfigEntry, ConfigEntry
from infinitewisdom.const import ALLOWED_CONFIG_FILE_PATHS, ALLOWED_CONFIG_FILE_EXTENSIONS, CONFIG_FILE_NAME, \
    CONFIG_NODE_ROOT, \
    CONFIG_NODE_IMAGE_ANALYSIS, CONFIG_NODE_PERSISTENCE, DEFAULT_SQL_PERSISTENCE_URL, \
    CONFIG_NODE_CRAWLER, CONFIG_NODE_TELEGRAM, CONFIG_NODE_GOOGLE_VISION, \
    CONFIG_NODE_TESSERACT, CONFIG_NODE_ENABLED, CONFIG_NODE_CAPACITY_PER_MONTH, CONFIG_NODE_INTERVAL, \
    CONFIG_NODE_UPLOADER, DEFAULT_FILE_PERSISTENCE_BASE_PATH, CONFIG_NODE_MICROSOFT_AZURE, CONFIG_NODE_PORT, \
    CONFIG_NODE_STATS


class Config:
    """
    Main InfiniteWisdom bot configuration
    """

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)

    TELEGRAM_BOT_TOKEN = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "bot_token"
        ],
        default="")

    TELEGRAM_INLINE_BADGE_SIZE = IntConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "inline_badge_size"
        ],
        default=16
    )

    TELEGRAM_GREETING_MESSAGE = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "greeting_message"
        ],
        default='Send /inspire for more inspiration :blush: Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.')

    TELEGRAM_CAPTION_IMAGES_WITH_TEXT = BoolConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_TELEGRAM,
            "caption_images_with_text"
        ],
        default=False)

    UPLOADER_INTERVAL = FloatConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_UPLOADER,
            CONFIG_NODE_INTERVAL
        ],
        default=1.0)

    UPLOADER_CHAT_ID = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_UPLOADER,
            "chat_id"
        ],
        default=None)

    CRAWLER_INTERVAL = FloatConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_CRAWLER,
            CONFIG_NODE_INTERVAL
        ],
        default=1.0)

    SQL_PERSISTENCE_URL = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "url"
        ],
        default=DEFAULT_SQL_PERSISTENCE_URL)

    FILE_PERSISTENCE_BASE_PATH = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "file_base_path"
        ],
        default=DEFAULT_FILE_PERSISTENCE_BASE_PATH)

    IMAGE_ANALYSIS_INTERVAL = FloatConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_INTERVAL
        ],
        default=1.0)

    IMAGE_ANALYSIS_TESSERACT_ENABLED = BoolConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_TESSERACT,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED = BoolConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            "auth_file"
        ],
        default=None)

    IMAGE_ANALYSIS_GOOGLE_VISION_CAPACITY = IntConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_GOOGLE_VISION,
            CONFIG_NODE_CAPACITY_PER_MONTH
        ],
        default=None)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_ENABLED = BoolConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            CONFIG_NODE_ENABLED
        ],
        default=False)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_SUBSCRIPTION_KEY = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            "subscription_key"
        ],
        default=None)

    IMAGE_ANALYSIS_MICROSOFT_AZURE_REGION = StringConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            "region"
        ],
        default="francecentral")

    IMAGE_ANALYSIS_MICROSOFT_AZURE_CAPACITY = IntConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            CONFIG_NODE_MICROSOFT_AZURE,
            CONFIG_NODE_CAPACITY_PER_MONTH
        ],
        default=5000)

    STATS_PORT = IntConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_STATS,
            CONFIG_NODE_PORT
        ],
        default=8000
    )

    def __init__(self):
        """
        Creates a config object and reads configuration.
        """
        self._config_entries = self._find_config_entries()
        self._read_yaml()
        self._read_env()
        self._validate()

    def _find_config_entries(self) -> [ConfigEntry]:
        """
        Detects config entry constants in this class
        :return: list of config entries
        """

        entries = set()
        for attribute in map(lambda x: getattr(self, x), dir(self)):
            if isinstance(attribute, ConfigEntry):
                entries.add(attribute)

        return list(entries)

    def _read_yaml(self) -> None:
        """
        Reads configuration parameters from a yaml config file (if it exists)
        """

        def _get_value(root: {}, config_entry: ConfigEntry):
            value = root
            for key in config_entry.yaml_path:
                value = value.get(key)
                if value is None:
                    return config_entry.value

            return value

        file_path = self._find_config_file()
        if file_path is None:
            self.LOGGER.debug("No config file found, skipping.")
            return

        with open(file_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
            if not cfg or CONFIG_NODE_ROOT not in cfg:
                return

            for entry in self._config_entries:
                entry.value = _get_value(cfg, entry)

    @staticmethod
    def _find_config_file() -> str or None:
        """
        Tries to find a usable config file
        :return: file path or None
        """
        for path in ALLOWED_CONFIG_FILE_PATHS:
            path = os.path.expanduser(path)
            for extension in ALLOWED_CONFIG_FILE_EXTENSIONS:
                file_path = os.path.join(path, "{}.{}".format(CONFIG_FILE_NAME, extension))
                if os.path.isfile(file_path):
                    return file_path

        return None

    def _read_env(self):
        """
        Reads configuration parameters from environment variables
        """
        for entry in self._config_entries:
            entry.value = os.environ.get(entry.env_key, entry.value)

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
