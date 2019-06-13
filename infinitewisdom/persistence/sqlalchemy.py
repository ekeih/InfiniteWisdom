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
import time
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from infinitewisdom.persistence import ImageDataPersistence, Entity

Base = declarative_base()


class Image(Base, Entity):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)

    url = Column(String)
    text = Column(String)
    analyser = Column(String)
    analyser_quality = Column(Float)
    created = Column(Float)
    telegram_file_id = Column(String)


class SQLAlchemyPersistence(ImageDataPersistence):
    """
    Implementation using SQLAlchemy
    """

    def __init__(self, url: str or None):
        if url is None:
            # TODO: extract to constant
            url = 'sqlite:///D:/tmp/infinitewisdom.db'

        self._engine = create_engine(url, echo=True)
        Base.metadata.create_all(self._engine)

        self._sessionmaker = sessionmaker(bind=self._engine)

    @contextmanager
    def _session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add(self, url: str, telegram_file_id: str or None, text: str = None, analyser: str = None,
            analyser_quality: float = None) -> bool:
        image = Image(url=url, telegram_file_id=telegram_file_id, text=text, analyser=analyser,
                      analyser_quality=analyser_quality, created=time.time())

        with self._session_scope() as session:
            session.add(image)

    def get_random(self, sample_size: int = None) -> Entity or [Entity]:
        with self._session_scope() as session:
            session.count()

    def find_by_url(self, url: str) -> [Entity]:
        with self._session_scope() as session:
            return [session.query(Image).filter_by(url=url).first()]

    def find_by_text(self, text: str = None, limit: int = None, offset: int = None) -> [Entity]:
        pass

    def count(self) -> int:
        with self._session_scope() as session:
            return session.query(Image).count()

    def update(self, entity: Entity) -> None:
        with self._session_scope() as session:
            old = session.query(Image).filter_by(url=url).first()
            old.telegram_file_id = entity.telegram_file_id
            old.analyser = entity.analyser
            old.analyser_quality = entity.analyser_quality
            old.text = entity.text

    def count_items_this_month(self, analyser: str) -> int:
        with self._session_scope() as session:
            return session.query(Image).filter(Image.analyser == analyser).filter(
                Image.created > (time.time() - 60 * 60 * 24 * 31)).first()

    def delete(self, url: str) -> None:
        with self._session_scope() as session:
            entity = self.find_by_url(url)
            if entity is not None:
                return session.delete(entity)

    def clear(self) -> None:
        pass
