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

    def add(self, entity: Entity) -> bool:
        """
        Persists a new entity
        :param entity: the entity to add
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
