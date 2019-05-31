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

DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH = "/tmp"

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

IMAGE_ANALYSIS_TYPE_TESSERACT = "tesseract"
IMAGE_ANALYSIS_TYPE_GOOGLE_VISION = "google-vision"
IMAGE_ANALYSIS_TYPE_BOTH = "both"

PERSISTENCE_TYPE_LOCAL = "local"

CONFIG_NODE_ROOT = "InfiniteWisdom"
CONFIG_NODE_PERSISTENCE = "persistence"
CONFIG_NODE_IMAGE_ANALYSIS = "image_analysis"
