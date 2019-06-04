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
import pickle
import random
import time
from collections import deque

from infinitewisdom.const import DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH
from infinitewisdom.stats import POOL_SIZE, TELEGRAM_ENTITIES_COUNT

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
        self.telegram_file_id = telegram_file_id


class ImageDataPersistence:
    """
    Persistence base class
    """

    def add(self, url: str, telegram_file_id: str or None, text: str = None, analyser: str = None,
            analyser_quality: float = None) -> bool:
        """
        Persists a new entity
        :param url: the image url
        :param telegram_file_id: file id of this image on telegram servers
        :param text: the text of the image
        :param analyser: an identifier for the analyser that was used to detect image text
        :param analyser_quality: quality of the analyser at this point in time
        :return: true when the entity was added, false otherwise
        """
        raise NotImplementedError()

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        """
        Returns a random entity
        :param sample_size: number of elements to return
        :return: the entity
        """
        raise NotImplementedError()

    def query(self, condition: callable, limit: int = None, offset: int = None) -> [Entity]:
        """
        Finds a list of entities that match the condition
        :param condition: condition to check
        :param limit: number of items to return (defaults to None)
        :param offset: item offset (defaults to 0)
        :return: list of entities
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
        raise NotImplementedError()

    def clear(self) -> None:
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


class LocalPersistence(ImageDataPersistence):
    """
    Implementation using a local file
    """

    FILE_NAME = "infinitewisdom.pickle"

    _entities = deque()

    def __init__(self, folder: str = None):
        if folder is None:
            folder = DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH

        if not os.path.exists(folder):
            raise FileNotFoundError("Path does not exist: {}".format(folder))
        if not os.path.isdir(folder):
            raise NotADirectoryError("Path is not a folder: {}".format(folder))

        self._file_path = os.path.join(folder, self.FILE_NAME)

        LOGGER.debug("Loading local persistence from: {}".format(self._file_path))
        self._load()

    def _load(self) -> None:
        """
        Loads the state from disk
        """
        if not os.path.exists(self._file_path):
            self._entities = deque()
            return

        if not os.path.isfile(self._file_path):
            raise AssertionError("Persistence target is not a file: {}".format(self._file_path))

        if not os.path.getsize(self._file_path) > 0:
            self._entities = deque()
            return

        with open(self._file_path, "rb") as file:
            self._entities = pickle.load(file)

        self._update_stats()
        LOGGER.debug("Local persistence loaded: {} entities".format(len(self._entities)))

    def _save(self) -> None:
        """
        Saves the current state to disk
        """
        with open(self._file_path, "wb") as file:
            pickle.dump(self._entities, file)

    def add(self, url: str, telegram_file_id: str or None, text: str = None, analyser: str = None,
            analyser_quality: float = None) -> bool:
        if len(self.find_by_url(url)) > 0:
            LOGGER.debug("Entity with url '{}' already in persistence, skipping.".format(url))
            return False

        entity = Entity(url, text, analyser, analyser_quality, time.time(), telegram_file_id)
        self._entities.insert(0, entity)
        self._save()
        self._update_stats()
        return True

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        if sample_size is None:
            return random.choice(self._entities)

        return random.sample(self._entities, k=sample_size)

    def query(self, condition: callable, limit: int = None, offset: int = None):
        if limit is None:
            limit = self.count()

        if offset is None:
            offset = 0

        start = offset
        end = offset + limit

        entities = list(filter(lambda x: condition(x), self._entities))
        return entities[start:end]

    def find_by_url(self, url: str) -> [Entity]:
        return self.query(lambda x: x.url == url)

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        if limit is None:
            limit = 16

        words = text.split(" ")
        return self.query(lambda x: self._contains_words(words, x.text), limit, offset)

    def count(self) -> int:
        return len(self._entities)

    def count_items_this_month(self, analyser: str) -> int:
        items = self.query(lambda x: x.analyser == analyser and x.created > (time.time() - 60 * 60 * 24 * 31))
        return len(items)

    def update(self, entity: Entity) -> None:
        old_entity = self.find_by_url(entity.url)[0]

        if old_entity is None:
            LOGGER.warning("No entity found for URL: {}".format(entity.url))
            return

        old_entity.telegram_file_id = entity.telegram_file_id
        old_entity.text = entity.text
        old_entity.analyser = entity.analyser
        self._save()
        self._update_stats()

    def delete(self, url: str):
        self._entities = self.query(lambda x: x.url is not url)
        self._save()
        self._update_stats()

    def clear(self) -> None:
        self._entities.clear()
        self._save()
        self._update_stats()

    def _update_stats(self):
        POOL_SIZE.set(self.count())
        uploaded_entites_count = len(self.query(lambda x: x.telegram_file_id is not None))
        TELEGRAM_ENTITIES_COUNT.set(uploaded_entites_count)
