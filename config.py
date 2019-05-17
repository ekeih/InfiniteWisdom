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

from const import ALLOWED_CONFIG_FILE_PATHS, ALLOWED_CONFIG_FILE_EXTENSIONS, CONFIG_FILE_NAME, CONFIG_NODE_ROOT, \
    CONFIG_NODE_BOT_TOKEN, CONFIG_NODE_GREETINGS_MESSAGE, CONFIG_NODE_IMAGE_POLLING_TIMEOUT, CONFIG_NODE_URL_POOL_SIZE, \
    ENV_PARAM_BOT_TOKEN, ENV_PARAM_GREETINGS_MESSAGE, ENV_PARAM_IMAGE_POLLING_TIMEOUT, ENV_PARAM_URL_POOL_SIZE


class Config:
    """
    Main InfiniteWisdom bot configuration
    """

    LOGGER = logging.getLogger(__name__)

    BOT_TOKEN = ""
    URL_POOL_SIZE = 10000
    IMAGE_POLLING_TIMEOUT = 1
    GREETING_MESSAGE = 'Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.'

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
        file_path = self._find_config_file()
        if file_path is None:
            self.LOGGER.debug("No config file found, skipping.")
            return

        with open(file_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
            if not cfg or CONFIG_NODE_ROOT not in cfg:
                return

            root = cfg[CONFIG_NODE_ROOT]
            self.BOT_TOKEN = root.get(CONFIG_NODE_BOT_TOKEN, self.BOT_TOKEN)
            self.GREETING_MESSAGE = root.get(CONFIG_NODE_GREETINGS_MESSAGE, self.GREETING_MESSAGE)
            self.URL_POOL_SIZE = root.get(CONFIG_NODE_URL_POOL_SIZE, self.URL_POOL_SIZE)
            self.IMAGE_POLLING_TIMEOUT = root.get(CONFIG_NODE_IMAGE_POLLING_TIMEOUT, self.IMAGE_POLLING_TIMEOUT)

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
        self.BOT_TOKEN = os.environ.get(ENV_PARAM_BOT_TOKEN, self.BOT_TOKEN)
        self.IMAGE_POLLING_TIMEOUT = os.environ.get(ENV_PARAM_IMAGE_POLLING_TIMEOUT, self.IMAGE_POLLING_TIMEOUT)
        self.GREETING_MESSAGE = os.environ.get(ENV_PARAM_GREETINGS_MESSAGE, self.GREETING_MESSAGE)
        self.URL_POOL_SIZE = os.environ.get(ENV_PARAM_URL_POOL_SIZE, self.URL_POOL_SIZE)

    def _validate(self):
        """
        Validates the current configuration and throws an exception if something is wrong
        """
        if len(self.BOT_TOKEN) <= 0:
            raise AssertionError("Bot token is missing!")
        if self.IMAGE_POLLING_TIMEOUT < 0:
            raise AssertionError("Image polling timeout must be >= 0!")
        if self.URL_POOL_SIZE < 0:
            raise AssertionError("URL pool size must be >= 0!")
