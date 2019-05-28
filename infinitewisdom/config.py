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

from infinitewisdom.const import ALLOWED_CONFIG_FILE_PATHS, ALLOWED_CONFIG_FILE_EXTENSIONS, CONFIG_FILE_NAME, \
    CONFIG_NODE_ROOT, \
    CONFIG_NODE_IMAGE_ANALYSIS, CONFIG_NODE_PERSISTENCE, DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH, PERSISTENCE_TYPE_LOCAL


class ConfigEntry:

    def __init__(self, yaml_path: [str], default: any = None):
        self.yaml_path = yaml_path
        self.env_key = "_".join(yaml_path).upper()
        self.default = default
        self.value = default


class Config:
    """
    Main InfiniteWisdom bot configuration
    """

    LOGGER = logging.getLogger(__name__)

    BOT_TOKEN = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            "bot_token"
        ],
        default="")

    URL_POOL_SIZE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            "max_url_pool_size"
        ],
        default=10000)

    IMAGE_POLLING_TIMEOUT = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            "image_polling_timeout"
        ],
        default=1)

    INLINE_BADGE_SIZE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            "inline_badge_size"
        ],
        default=16
    )

    GREETING_MESSAGE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            "greeting_message"
        ],
        default='Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.')

    PERSISTENCE_TYPE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "type"
        ],
        default=PERSISTENCE_TYPE_LOCAL)

    LOCAL_PERSISTENCE_FOLDER_PATH = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_PERSISTENCE,
            "path"
        ],
        default=DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH)

    IMAGE_ANALYSIS_TYPE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            "type"
        ],
        default=None)

    IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE = ConfigEntry(
        yaml_path=[
            CONFIG_NODE_ROOT,
            CONFIG_NODE_IMAGE_ANALYSIS,
            "auth_file"
        ],
        default=None)

    _config_entries = [BOT_TOKEN, URL_POOL_SIZE, IMAGE_POLLING_TIMEOUT, GREETING_MESSAGE, INLINE_BADGE_SIZE,
                       PERSISTENCE_TYPE, LOCAL_PERSISTENCE_FOLDER_PATH,
                       IMAGE_ANALYSIS_TYPE, IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE]

    def __init__(self):
        """
        Creates a config object and reads configuration.
        """
        self._read_yaml()
        self._read_env()
        self._validate()

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
        if len(self.BOT_TOKEN.value) <= 0:
            raise AssertionError("Bot token is missing!")
        if self.IMAGE_POLLING_TIMEOUT.value < 0:
            raise AssertionError("Image polling timeout must be >= 0!")
        if self.URL_POOL_SIZE.value < 0:
            raise AssertionError("URL pool size must be >= 0!")

        if not os.path.exists(self.LOCAL_PERSISTENCE_FOLDER_PATH.value):
            raise FileNotFoundError(
                "Local persistence path does not exist: {}".format(self.LOCAL_PERSISTENCE_FOLDER_PATH.value))
        if not os.path.isdir(self.LOCAL_PERSISTENCE_FOLDER_PATH.value):
            raise NotADirectoryError(
                "Local persistence path is not a folder: {}".format(self.LOCAL_PERSISTENCE_FOLDER_PATH.value))

        if not os.path.isfile(self.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value):
            raise IsADirectoryError("Google Vision Auth file path is not a file: {}".format(
                self.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value))
