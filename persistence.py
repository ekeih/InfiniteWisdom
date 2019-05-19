import os
import pickle
import random

from const import DEFAULT_LOCAL_PERSISTENCE_FOLDER_PATH


class Entity:
    """
    Persistence entity
    """

    def __init__(self, url: str, text: str = None):
        self.url = url
        self.text = text


class ImageUrlPersistence:
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

    def find_by_text(self, text: str = None) -> [Entity]:
        """
        Finds a list of entities containing the given text
        :param text: the text to search for
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

    def clear(self) -> None:
        """
        Removes all entries from the persistence
        """
        raise NotImplementedError()


class LocalPersistence(ImageUrlPersistence):
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

    def _save(self) -> None:
        """
        Saves the current state to disk
        """
        with open(self._file_path, "wb") as file:
            pickle.dump(self._entities, file)

    def add(self, url: str, text: str = None) -> None:
        entity = Entity(url, text)
        self._entities.append(entity)
        self._save()

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        if sample_size is None:
            return random.choice(self._entities)

        return random.sample(self._entities, k=sample_size)

    def find_by_text(self, text: str = None) -> [Entity]:
        return list(filter(lambda x: text in x.text, self._entities))

    def count(self) -> int:
        return len(self._entities)

    def clear(self) -> None:
        self._entities.clear()
        self._save()
