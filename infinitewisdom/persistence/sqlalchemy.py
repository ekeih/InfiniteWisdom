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
import time
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, func, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from infinitewisdom.const import DEFAULT_SQL_PERSISTENCE_URL

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

Base = declarative_base()


class Entity:
    """
    Persistence entity
    """

    def __init__(self, url: str, created: float, text: str or None = None, analyser: str or None = None,
                 analyser_quality: float or None = None, image_hash: str or None = None,
                 telegram_file_id: str or None = None):
        self.url = url
        self.text = text
        self.analyser = analyser
        self._analyser_quality = analyser_quality
        self.created = created
        self._telegram_file_id = telegram_file_id
        self._image_hash = image_hash

    @property
    def id(self):
        return self.__dict__.get('id', None)

    @property
    def telegram_file_id(self):
        return self.__dict__.get('telegram_file_id', None)

    @telegram_file_id.setter
    def telegram_file_id(self, value):
        self._telegram_file_id = value

    @property
    def analyser_quality(self):
        return self.__dict__.get('analyser_quality', None)

    @analyser_quality.setter
    def analyser_quality(self, value):
        self._analyser_quality = value

    @property
    def image_hash(self):
        return self.__dict__.get('image_hash', None)

    @image_hash.setter
    def image_hash(self, value):
        self._image_hash = value


class Image(Base, Entity):
    """
    Data model of a single quote
    """
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)

    url = Column(String)
    text = Column(String)
    analyser = Column(String)
    analyser_quality = Column(Float)
    created = Column(Float)
    telegram_file_id = Column(String)
    image_hash = Column(String)


class SQLAlchemyPersistence:
    """
    Implementation using SQLAlchemy
    """

    def __init__(self, url: str or None = None):
        if url is None:
            url = DEFAULT_SQL_PERSISTENCE_URL

        self._engine = create_engine(url, echo=False)
        Base.metadata.create_all(self._engine)

        self._sessionmaker = sessionmaker(bind=self._engine)

        LOGGER.debug("SQLAlchemy persistence loaded: {} entities".format(self.count()))

    @contextmanager
    def _session_scope(self, write: bool = False) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self._sessionmaker()
        try:
            yield session
            if write:
                session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_all(self) -> [Entity]:
        with self._session_scope() as session:
            return session.query(Image).order_by(Image.id).all()

    def add(self, entity: Entity):
        image = Image(url=entity.url,
                      text=entity.text,
                      analyser=entity.analyser, analyser_quality=entity.analyser_quality,
                      telegram_file_id=entity.telegram_file_id,
                      image_hash=entity.image_hash,
                      created=entity.created)

        with self._session_scope() as session:
            session.add(image)
            session.commit()
            session.refresh(image)
            return image

    def get_random(self, page_size: int = None) -> Entity or [Entity]:
        with self._session_scope() as session:
            query = session.query(Image).order_by(func.random()).limit(page_size)
            if page_size is None:
                return query.first()
            else:
                return query.all()

    def find_by_image_hash(self, image_hash: str) -> Entity or None:
        with self._session_scope() as session:
            return session.query(Image).filter_by(image_hash=image_hash).first()

    def find_by_url(self, url: str) -> [Entity]:
        with self._session_scope() as session:
            return session.query(Image).filter_by(url=url).all()

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        if limit is None:
            limit = 16

        words = text.split(" ")

        with self._session_scope() as session:
            filters = list(map(lambda word: Image.text.ilike("%{}%".format(word)), words))
            return session.query(Image).filter(and_(*filters)).limit(limit).offset(offset).all()

    def find_non_optimal(self, target_quality: int) -> Entity or None:
        with self._session_scope() as session:
            entity = session.query(Image).filter(Image.analyser_quality.is_(None)).order_by(
                Image.created).first()
            if entity is not None:
                return entity

            return session.query(Image).filter(Image.analyser_quality.isnot(None),
                                               Image.analyser_quality < target_quality).order_by(
                Image.analyser_quality,
                Image.created).first()

    def find_without_image_data(self) -> Entity or None:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.image_hash.is_(None)).order_by(
                Image.created).all()

    def find_not_uploaded(self) -> Entity or None:
        with self._session_scope() as session:
            return session.query(Image).filter(
                and_(Image.telegram_file_id.is_(None),
                     Image.image_hash.isnot(None))).order_by(Image.created).first()

    def count(self) -> int:
        with self._session_scope() as session:
            return session.query(Image).count()

    def update(self, entity: Entity) -> None:
        with self._session_scope(write=True) as session:
            old = session.query(Image).with_for_update().filter_by(id=entity.id).first()
            old.telegram_file_id = entity.telegram_file_id
            old.analyser = entity.analyser
            old.analyser_quality = entity.analyser_quality
            old.text = entity.text
            old.image_hash = entity.image_hash

    def count_items_this_month(self, analyser: str) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.analyser == analyser).filter(
                Image.created > (time.time() - 60 * 60 * 24 * 31)).count()

    def delete(self, url: str) -> None:
        with self._session_scope(write=True) as session:
            entity = session.query(Image).filter_by(url=url).first()
            if entity is not None:
                return session.delete(entity)

    def clear(self) -> None:
        raise NotImplementedError()

    def count_items_with_telegram_upload(self) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.telegram_file_id.isnot(None)).count()

    def count_items_by_analyser(self, analyser_id: str) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.analyser == analyser_id).count()

    def count_items_with_text(self) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(func.length(Image.text) > 0).count()

    def count_items_with_image_data(self) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.image_hash.isnot(None)).count()
