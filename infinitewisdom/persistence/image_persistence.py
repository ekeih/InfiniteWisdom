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
from threading import Lock

lock = Lock()


class ImageDataStore:
    """
    Image data store
    """

    def __init__(self, base_path: str):
        self._base_path = base_path

    def get(self, image_hash: str) -> bytes or None:
        """
        Get the image data for a database entity
        :param image_hash: expected image hash
        :return: image bytes or None if no data exist
        """
        with lock:
            if image_hash is None:
                return None

            file_path = self._get_file_path(image_hash)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            else:
                return None

    def put(self, image_hash: str, image_data: bytes or None):
        """
        Stores image data for
        :param image_hash: the image hash
        :param image_data: the image data
        """
        with lock:
            file_path = self._get_file_path(image_hash)
            folder, file = os.path.split(file_path)

            if image_data is None:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(folder) and len(os.listdir(folder)) == 0:
                    os.remove(folder)
            else:
                os.makedirs(folder, exist_ok=True)

                with open(file_path, 'wb') as f:
                    f.write(image_data)

    def clear(self):
        with lock:
            raise NotImplementedError()

    def _get_file_path(self, image_hash) -> os.path:
        """
        Constructs the file path where the image date is located
        :param image_hash: image hash
        :return: file path
        """
        return os.path.abspath(os.path.join(self._base_path, image_hash[:2], "{}.jpg".format(image_hash)))
