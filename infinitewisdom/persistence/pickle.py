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

from infinitewisdom.const import DEFAULT_PICKLE_PERSISTENCE_PATH
from infinitewisdom.persistence import ImageDataPersistence, Entity

LOGGER = logging.getLogger(__name__)


class PicklePersistence(ImageDataPersistence):
    """
    Implementation using a local file
    """

    _entities = deque()

    def __init__(self, path: str = None):
        if path is None:
            path = DEFAULT_PICKLE_PERSISTENCE_PATH

        if not os.path.exists(path):
            raise FileNotFoundError("Path does not exist: {}".format(path))
        if not os.path.isfile(path):
            raise NotADirectoryError("Path is not a file: {}".format(path))

        self._file_path = path

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

    def _add(self, entity: Entity) -> bool:
        if len(self.find_by_url(entity.url)) > 0:
            LOGGER.debug("Entity with url '{}' already in persistence, skipping.".format(entity.url))
            return False

        self._entities.insert(0, entity)
        self._save()
        return True

    def get_random(self, page_size: int = None) -> Entity or [Entity]:
        if page_size is None:
            return random.choice(self._entities)

        return random.sample(self._entities, k=page_size)

    def _query(self, condition: callable, limit: int = None, offset: int = None):
        """
        Finds a list of entities that match the condition
        :param condition: condition to check
        :param limit: number of items to return (defaults to None)
        :param offset: item offset (defaults to 0)
        :return: list of entities
        """

        if limit is None:
            limit = self.count()

        if offset is None:
            offset = 0

        start = offset
        end = offset + limit

        entities = list(filter(lambda x: condition(x), self._entities))
        return entities[start:end]

    def find_by_url(self, url: str) -> [Entity]:
        return self._query(lambda x: x.url == url)

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        if limit is None:
            limit = 16

        words = text.split(" ")
        return self._query(lambda x: self._contains_words(words, x.text), limit, offset)

    def count(self) -> int:
        return len(self._entities)

    def count_items_this_month(self, analyser: str) -> int:
        items = self._query(lambda x: x.analyser == analyser and x.created > (time.time() - 60 * 60 * 24 * 31))
        return len(items)

    def _update(self, entity: Entity) -> None:
        old_entity = self.find_by_url(entity.url)[0]

        if old_entity is None:
            LOGGER.warning("No entity found for URL: {}".format(entity.url))
            return

        old_entity.telegram_file_id = entity.telegram_file_id
        old_entity.text = entity.text
        old_entity.analyser = entity.analyser
        self._save()

    def _delete(self, url: str):
        self._entities = self._query(lambda x: x.url is not url)
        self._save()

    def _clear(self) -> None:
        self._entities.clear()
        self._save()

    def count_items_with_telegram_upload(self) -> int:
        return len(self._query(lambda x: x.telegram_file_id is not None))

    def count_items_by_analyser(self, analyser_id: str) -> int:
        return len(self._query(lambda x: x.analyser == analyser_id))

    def count_items_with_text(self) -> int:
        return len(self._query(lambda x: x.text is not None and len(x.text) > 0))
