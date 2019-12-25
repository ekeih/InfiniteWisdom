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
import threading
import time

from telegram import Bot

from infinitewisdom import RegularIntervalWorker
from infinitewisdom.config.config import AppConfig
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.stats import UPLOADER_TIME
from infinitewisdom.util import send_photo, download_image_bytes

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

lock = threading.Lock()


class TelegramUploader(RegularIntervalWorker):
    """
    Worker that sends every image that has not yet been uploaded to telegram servers to a specified chat
    to use telegram backend for as image hoster.
    """

    def __init__(self, config: AppConfig, persistence: ImageDataPersistence, bot: Bot):
        super().__init__(config.UPLOADER_INTERVAL.value)
        self._persistence = persistence
        self._bot = bot
        self._chat_id = config.UPLOADER_CHAT_ID.value

    def start(self):
        if self._chat_id is None:
            LOGGER.debug("No chat id configured, not starting uploader.")
            return
        super().start()

    @UPLOADER_TIME.time()
    def _run(self):
        with lock:
            entity = self._persistence.find_not_uploaded()
            if entity is None:
                # sleep for a longer time period to reduce load
                time.sleep(60)
                return

            image_data = self._persistence._image_data_store.get(entity.image_hash)
            if image_data is None:
                LOGGER.warning("Missing image data for entity, trying to download: {}".format(entity))
                try:
                    image_data = download_image_bytes(entity.url)
                    self._persistence.update(entity, image_data)
                except Exception as e:
                    LOGGER.error(
                        "Error trying to download missing image data for url '{}', deleting entity.".format(entity.url),
                        e)
                    self._persistence.delete(entity)
                return

            file_ids = send_photo(bot=self._bot, chat_id=self._chat_id, image_data=image_data)
            for file_id in file_ids:
                entity.add_file_id(file_id)
            self._persistence.update(entity, image_data)
            LOGGER.debug(
                "Send image '{}' to chat '{}' and updated entity with file_id {}.".format(
                    entity.url, self._chat_id, file_ids))
