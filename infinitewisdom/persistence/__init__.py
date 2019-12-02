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

from infinitewisdom.config.config import AppConfig
from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_TESSERACT, IMAGE_ANALYSIS_TYPE_GOOGLE_VISION, \
    IMAGE_ANALYSIS_TYPE_AZURE, IMAGE_ANALYSIS_TYPE_HUMAN
from infinitewisdom.persistence.image_persistence import ImageDataStore
from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence, Image
from infinitewisdom.stats import POOL_SIZE, TELEGRAM_ENTITIES_COUNT, IMAGE_ANALYSIS_TYPE_COUNT, \
    IMAGE_ANALYSIS_HAS_TEXT_COUNT, ENTITIES_WITH_IMAGE_DATA_COUNT
from infinitewisdom.util import create_hash

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

lock = threading.RLock()


class ImageDataPersistence:
    """
    Persistence main class
    """

    def __init__(self, config: AppConfig):
        self._config = config

        self._database = SQLAlchemyPersistence(config.SQL_PERSISTENCE_URL.value)
        self._image_data_store = ImageDataStore(config.FILE_PERSISTENCE_BASE_PATH.value)

        self._update_stats()

    def get_all(self) -> [Image]:
        """
        :return: a list of all entities
        """
        return self._database.get_all()

    def add(self, image: Image, image_data: bytes) -> None:
        """
        Persists a new entity
        :param image: the entity to add
        :param image_data: image data
        """
        with lock:
            try:
                image_hash = create_hash(image_data)
                image.image_hash = image_hash
                self._database.add(image)
                self._image_data_store.put(image_hash, image_data)
            finally:
                self._update_stats()

    def get_image_data(self, entity: Image) -> bytes or None:
        """
        Get the image data for an entity
        :param entity: the entity to get the image for
        :return: image data or None
        """
        return self._image_data_store.get(entity.image_hash)

    def get_random(self, page_size: int = None) -> Image or [Image]:
        """
        Returns a random entity or number of random entities depending on parameters.
        If a page_size is specified a list of entities will be returned, otherwise a single entity or None.
        :param page_size: number of elements to return
        :return: the entity
        """
        return self._database.get_random(page_size)

    def find_by_url(self, url: str) -> [Image]:
        """
        Finds a list of entities with exactly the given url
        :param url: the url to search for
        :return: list of entities
        """
        return self._database.find_by_url(url)

    def find_by_image_hash(self, image_hash: str) -> Image or None:
        """
        Finds an entity with exactly the given image_hash
        :param image_hash: the image hash to search for
        :return: entity or None
        """
        with lock:
            return self._database.find_by_image_hash(image_hash)

    def find_by_telegram_file_id(self, telegram_file_id: str) -> Image or None:
        """
        Finds an entity with exactly the given telegram file id
        :param telegram_file_id: the image hash to search for
        :return: entity or None
        """
        return self._database.find_by_telegram_file_id(telegram_file_id)

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Image]:
        """
        Finds a list of entities containing the given text
        :param text: the text to search for
        :param limit: number of items to return (defaults to 16)
        :param offset: item offset
        :return: list of entities
        """
        return self._database.find_by_text(text, limit, offset)

    def find_non_optimal(self, target_quality: int) -> Image or None:
        """
        Finds an image with suboptimal analysis quality.

        If multiple images exist they are sorted by the following criteria:
          - quality (None first, lowest first)
          - date (oldest first)

        :param target_quality: the target quality to reach
        :return: a non-optimal entity or None
        """
        with lock:
            return self._database.find_first_non_optimal(target_quality)

    def find_without_image_data(self) -> [Image]:
        """
        Finds entities without image data
        :return: list of entities without image data
        """
        with lock:
            return self._database.find_without_image_data()

    def find_not_uploaded(self) -> Image or None:
        """
        Finds an image that has not yet been uploaded to telegram servers
        :return: entity or None
        """
        with lock:
            return self._database.find_not_uploaded()

    def count(self) -> int:
        """
        Returns the total number of entities stored in this persistence
        :return: total count
        """
        return self._database.count()

    def update(self, entity: Image, image_data: bytes or None = None) -> None:
        """
        Updates the given entity
        :param entity: the entity with modified fields
        :param image_data: the image data of the entity, passing None will not change existing image data
        """
        with lock:
            try:
                existing_entity = self._database.find_by_image_hash(entity.image_hash)

                new_hash = None
                if image_data is not None:
                    new_hash = create_hash(image_data)

                if new_hash is not None and existing_entity.image_hash != new_hash:
                    LOGGER.debug(
                        "Hash changed from {} to {} for entity with url: {}".format(existing_entity.image_hash,
                                                                                    new_hash,
                                                                                    entity.url))
                    entity.image_hash = new_hash
                if self._image_data_store.get(entity.image_hash) is None:
                    self._image_data_store.put(entity.image_hash, image_data)
                    LOGGER.debug("Saved new image data for hash: {}".format(entity.image_hash))
                self._database.update(entity)
            finally:
                self._update_stats()

    def count_items_this_month(self, analyser: str) -> int:
        """
        Returns the number of items added this month by the given analyser
        :param analyser: analyser to check
        :return: number of items
        """
        return self._database.count_items_this_month(analyser)

    def delete(self, entity: Image) -> None:
        """
        Removes an entity from the persistence
        :param entity: the entity to delete
        """
        with lock:
            try:
                entity = self._database.find_by_image_hash(entity.image_hash)
                if entity is not None:
                    self._image_data_store.put(entity.image_hash, None)
                    self._database.delete(entity.id)
            finally:
                self._update_stats()

    def clear(self) -> None:
        """
        Removes all entries from the persistence
        """
        with lock:
            try:
                self._database.clear()
                self._image_data_store.clear()
            finally:
                self._update_stats()

    @staticmethod
    def _contains_words(words: [str], text):
        """
        Checks if the given text contains all of the given words ignoring case
        :param words: words to check for
        :param text: text to analyse
        :return: True if the text contains all of the given words, false otherwise
        """

        if text is None:
            return False
        text = text.lower()

        for word in words:
            if word.lower() not in text:
                return False

        return True

    def _update_stats(self):
        """
        Updates prometheus statistics related to persistence
        """
        POOL_SIZE.set(self.count())

        entites_with_image_data_count = self.count_items_with_image_data()
        ENTITIES_WITH_IMAGE_DATA_COUNT.set(entites_with_image_data_count)

        uploaded_entites_count = self.count_items_with_telegram_upload()
        TELEGRAM_ENTITIES_COUNT.set(uploaded_entites_count)

        tesseract_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_TESSERACT)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_TESSERACT).set(tesseract_entites_count)

        google_vision_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_GOOGLE_VISION)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_GOOGLE_VISION).set(google_vision_entites_count)

        microsoft_azure_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_AZURE)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_AZURE).set(microsoft_azure_entites_count)

        human_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_HUMAN)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_HUMAN).set(human_entites_count)

        entities_with_text_count = self.count_items_with_text()
        IMAGE_ANALYSIS_HAS_TEXT_COUNT.set(entities_with_text_count)

    def count_items_with_telegram_upload(self) -> int:
        """
        :return: the number of images that have been uploaded to telegram servers
        """
        return self._database.count_items_with_telegram_upload()

    def count_items_by_analyser(self, analyser_id: str) -> int:
        """
        :param analyser_id: analyser id to count
        :return: the number of images that have been analysed by the given analyser
        """
        return self._database.count_items_by_analyser(analyser_id)

    def count_items_with_text(self) -> int:
        """
        :return: the number of images that have a text
        """
        return self._database.count_items_with_text()

    def count_items_with_image_data(self) -> int:
        """
        :return: the number of images that have a image data
        """
        return self._database.count_items_with_image_data()
