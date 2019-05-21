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

from const import DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH
from stats import POOL_SIZE

LOGGER = logging.getLogger(__name__)


class Entity:
    """
    Persistence entity
    """

    def __init__(self, url: str, text: str = None):
        self.url = url
        self.text = text


class ImageDataPersistence:
    """
    Persistence base class
    """

    def add(self, url: str, text: str = None) -> None:
        """
        Persists a new entity
        :param url: the image url
        :param text: the text of the image
        """
        raise NotImplementedError()

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        """
        Returns a random entity
        :param sample_size: number of elements to return
        :return: the entity
        """
        raise NotImplementedError()

    def find_by_text(self, text: str = None, limit: int = None, offset: int = 0) -> [Entity]:
        """
        Finds a list of entities containing the given text
        :param text: the text to search for
        :param limit: number of items to return
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
        Checks if the given text contains at least one of the given words ignoring case
        :param words: words to check for
        :param text: text to analyse
        :return: True if the text contains at least one of the given words, false otherwise
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

    _entities = []

    def __init__(self, file_path: str = None):
        if file_path is not None:
            self._file_path = file_path
        else:
            self._file_path = os.path.join(DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH, self.FILE_NAME)

        LOGGER.debug("Loading local persistence from: {}".format(self._file_path))
        self._load()

    def _load(self) -> None:
        """
        Loads the state from disk
        """
        if not os.path.exists(self._file_path):
            self._entities = []
            return

        if not os.path.isfile(self._file_path):
            raise AssertionError("Persistence target is not a file: {}".format(self._file_path))

        if not os.path.getsize(self._file_path) > 0:
            self._entities = []
            return

        with open(self._file_path, "rb") as file:
            self._entities = pickle.load(file)

        POOL_SIZE.set(self.count())
        LOGGER.debug("Local persistence loaded: {} entities".format(len(self._entities)))

    def _save(self) -> None:
        """
        Saves the current state to disk
        """
        with open(self._file_path, "wb") as file:
            pickle.dump(self._entities, file)

    def add(self, url: str, text: str = None) -> None:
        entity = Entity(url, text)
        self._entities.append(entity)
        POOL_SIZE.set(self.count())
        self._save()

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        if sample_size is None:
            return random.choice(self._entities)

        return random.sample(self._entities, k=sample_size)

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        if limit is None:
            limit = 16
        if offset is None:
            offset = 0

        words = text.split(" ")
        return list(filter(lambda x: self._contains_words(words, x.text), self._entities))[offset:offset + limit]

    def count(self) -> int:
        return len(self._entities)

    def delete(self, url: str):
        self._entities = list(filter(lambda x: x.url is not url, self._entities))
        POOL_SIZE.set(self.count())
        self._save()

    def clear(self) -> None:
        self._entities.clear()
        POOL_SIZE.set(self.count())
        self._save()
