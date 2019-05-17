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

"""
Holds important constants
"""

CONFIG_FILE_NAME = "infinitewisdom"

# the order of this list also defines priority
ALLOWED_CONFIG_FILE_EXTENSIONS = [
    "yaml",
    "yml"
]

# the order of this list also defines priority
ALLOWED_CONFIG_FILE_PATHS = [
    "./",
    "~/.config/",
    "~/"
]

CONFIG_NODE_ROOT = "InfiniteWisdom"
CONFIG_NODE_BOT_TOKEN = "bot_token"
CONFIG_NODE_GREETINGS_MESSAGE = "greetings_message"
CONFIG_NODE_URL_POOL_SIZE = "max_url_pool_size"
CONFIG_NODE_IMAGE_POLLING_TIMEOUT = "image_polling_timeout"

# environment variables
ENV_PARAM_BOT_TOKEN = 'BOT_TOKEN'
ENV_PARAM_IMAGE_POLLING_TIMEOUT = 'IMAGE_POLLING_TIMEOUT'
ENV_PARAM_URL_POOL_SIZE = 'URL_POOL_SIZE'
ENV_PARAM_GREETINGS_MESSAGE = 'GREETINGS_MESSAGE'
