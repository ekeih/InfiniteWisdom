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

from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_TESSERACT, IMAGE_ANALYSIS_TYPE_GOOGLE_VISION
from infinitewisdom.stats import POOL_SIZE, TELEGRAM_ENTITIES_COUNT, IMAGE_ANALYSIS_TYPE_COUNT, \
    IMAGE_ANALYSIS_HAS_TEXT_COUNT

LOGGER = logging.getLogger(__name__)


class Entity:
    """
    Persistence entity
    """

    def __init__(self, url: str, text: str, analyser: str, analyser_quality: float, created: float,
                 telegram_file_id: str or None):
        self.url = url
        self.text = text
        self.analyser = analyser
        self.analyser_quality = analyser_quality
        self.created = created
        self._telegram_file_id = telegram_file_id

    @property
    def telegram_file_id(self):
        return self.__dict__.get('telegram_file_id', None)

    @telegram_file_id.setter
    def telegram_file_id(self, value):
        self._telegram_file_id = value


class ImageDataPersistence:
    """
    Persistence base class
    """

    def add(self, entity: Entity) -> bool:
        """
        Persists a new entity
        :param entity: the entity to add
        :return: true when the entity was added, false otherwise
        """
        try:
            if len(self.find_by_url(entity.url)) > 0:
                LOGGER.debug("Entity with url '{}' already in persistence, skipping.".format(entity.url))
                return False

            return self._add(entity)
        finally:
            self._update_stats()

    def _add(self, entity: Entity) -> bool:
        """
        Persists a new entity
        :param entity: the entity to add
        :return: true when the entity was added, false otherwise
        """
        raise NotImplementedError()

    def get_random(self, page_size: int = None) -> Entity or [Entity]:
        """
        Returns a random entity or number of random entities depending on parameters.
        If a page_size is specified a list of entities will be returned, otherwise a single entity or None.
        :param page_size: number of elements to return
        :return: the entity
        """
        raise NotImplementedError()

    def find_by_url(self, url: str) -> [Entity]:
        """
        Finds a list of entities with exactly the given url
        :param url: the url to search for
        :return: list of entities
        """
        raise NotImplementedError()

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        """
        Finds a list of entities containing the given text
        :param text: the text to search for
        :param limit: number of items to return (defaults to 16)
        :param offset: item offset
        :return: list of entities
        """
        raise NotImplementedError()

    def find_non_optimal(self, target_quality: int) -> Entity or None:
        """
        Finds an image with suboptimal analysis quality.

        If multiple images exist they are sorted by the following criteria:
          - quality (None first, lowest first)
          - date (oldest first)

        :param target_quality: the target quality to reach
        :return: a non-optimal entity or None
        """
        raise NotImplementedError()

    def count(self) -> int:
        """
        Returns the total number of entities stored in this persistence
        :return: total count
        """
        raise NotImplementedError()

    def update(self, entity: Entity) -> None:
        """
        Updates the given entity
        :param entity: the entity with modified fields
        """
        try:
            self._update(entity)
        finally:
            self._update_stats()

    def _update(self, entity: Entity) -> None:
        """
        Updates the given entity
        :param entity: the entity with modified fields
        """
        raise NotImplementedError()

    def count_items_this_month(self, analyser: str) -> int:
        """
        Returns the number of items added this month by the given analyser
        :param analyser: analyser to check
        :return: number of items
        """
        raise NotImplementedError()

    def delete(self, url: str) -> None:
        """
        Removes an entity from the persistence
        :param url: the image url
        """
        try:
            self._delete(url)
        finally:
            self._update_stats()

    def _delete(self, url: str) -> None:
        """
        Removes an entity from the persistence
        :param url: the image url
        """
        raise NotImplementedError()

    def clear(self) -> None:
        """
        Removes all entries from the persistence
        """
        try:
            self._clear()
        finally:
            self._update_stats()

    def _clear(self) -> None:
        """
        Removes all entries from the persistence
        """
        raise NotImplementedError()

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

        uploaded_entites_count = self.count_items_with_telegram_upload()
        TELEGRAM_ENTITIES_COUNT.set(uploaded_entites_count)

        tesseract_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_TESSERACT)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_TESSERACT).set(tesseract_entites_count)

        google_vision_entites_count = self.count_items_by_analyser(IMAGE_ANALYSIS_TYPE_GOOGLE_VISION)
        IMAGE_ANALYSIS_TYPE_COUNT.labels(type=IMAGE_ANALYSIS_TYPE_GOOGLE_VISION).set(google_vision_entites_count)

        entities_with_text_count = self.count_items_with_text()
        IMAGE_ANALYSIS_HAS_TEXT_COUNT.set(entities_with_text_count)

    def count_items_with_telegram_upload(self) -> int:
        """
        :return: the number of images that have been uploaded to telegram servers
        """
        raise NotImplementedError()

    def count_items_by_analyser(self, analyser_id: str) -> int:
        """
        :param analyser_id: analyser id to count
        :return: the number of images that have been analysed by the given analyser
        """
        raise NotImplementedError()

    def count_items_with_text(self) -> int:
        """
        :return: the number of images that have a text
        """
        raise NotImplementedError()
