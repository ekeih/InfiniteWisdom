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
from collections import Counter
from datetime import datetime

from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float, func, and_, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

from infinitewisdom.const import DEFAULT_SQL_PERSISTENCE_URL
from infinitewisdom.util import cryptographic_hash

LOGGER = logging.getLogger(__name__)

Base = declarative_base()

association_table = Table(
    'association', Base.metadata,
    Column('bot_token_id', Integer, ForeignKey('bot_tokens.id')),
    Column('telegram_file_id_id', String, ForeignKey('telegram_file_ids.id'))
)


class BotToken(Base):
    """
    Data model of a (hashed) bot token
    """
    __tablename__ = 'bot_tokens'

    id = Column(Integer, primary_key=True)
    hashed_token = Column(String, unique=True)
    telegram_file_ids = relationship("TelegramFileId",
                                     secondary=association_table,
                                     back_populates="bot_tokens")


class Image(Base):
    """
    Data model of a single quote
    """
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)

    url = Column(String, index=True)
    text = Column(String)
    analyser = Column(String)
    analyser_quality = Column(Float)
    created = Column(Float)
    image_hash = Column(String, index=True)
    telegram_file_ids = relationship("TelegramFileId",
                                     back_populates="image",
                                     single_parent=True,
                                     cascade="all, delete-orphan",
                                     lazy="joined")

    def __str__(self):
        return ", ".join(
            ["Created: `{}`".format(datetime.fromtimestamp(self.created)),
             "URL: {}".format(self.url),
             "Telegram file ids: [{}]".format(", ".join(list(map(lambda x: x.id, self.telegram_file_ids)))),
             "Hash: {}".format(self.image_hash),
             "Analyser: {}".format(self.analyser),
             "Analyser quality: {}".format(self.analyser_quality),
             "Text: `{}`".format(self.text)])

    def add_file_id(self, bot_token: BotToken, file_id: str):
        """
        Adds a file id to the database
        :param bot_token: the bot token that was used to upload the image
        :param file_id: the file id
        """
        existing = list(filter(lambda x: x.id == file_id, self.telegram_file_ids))
        if len(existing) > 0:
            # update existing entity with (possibly) new bot_token
            e = existing[0]
            bot_token_entities = list(filter(lambda x: x.hashed_token == bot_token.hashed_token, e.bot_tokens))
            if len(bot_token_entities) <= 0:
                e.bot_tokens.append(bot_token)
        else:
            # add new file_id
            file_id_entity = TelegramFileId(id=file_id, image_id=self.id)
            file_id_entity.bot_tokens.append(bot_token)
            file_ids = {file_id_entity}
            file_ids.update(self.telegram_file_ids)
            self.telegram_file_ids = list(file_ids)


class TelegramFileId(Base):
    """
    Data model of a telegram file id
    """
    __tablename__ = 'telegram_file_ids'

    id = Column(String, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'))
    bot_tokens = relationship("BotToken",
                              secondary=association_table,
                              back_populates="telegram_file_ids",
                              lazy="joined")
    image = relationship("Image", back_populates="telegram_file_ids")


_sessionmaker = sessionmaker()


@contextmanager
def _session_scope(write: bool = True) -> Session:
    """Provide a transactional scope around a series of operations."""
    session = _sessionmaker()
    try:
        yield session
        if write:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SQLAlchemyPersistence:
    """
    Implementation using SQLAlchemy
    """

    def __init__(self, url: str or None = None):
        if url is None:
            url = DEFAULT_SQL_PERSISTENCE_URL

        # TODO: this currently also logs to file because of alembic
        self._migrate_db(url)

        global _sessionmaker
        engine = create_engine(url)
        _sessionmaker.configure(bind=engine)

        with _session_scope() as session:
            LOGGER.debug("SQLAlchemy persistence loaded: {} entities".format(self.count(session)))

    @staticmethod
    def _migrate_db(url: str):
        from alembic.config import Config
        import alembic.command

        config = Config('alembic.ini')
        config.set_main_option('sqlalchemy.url', url)
        config.attributes['configure_logger'] = False

        alembic.command.upgrade(config, 'head')

    @staticmethod
    def get_or_add_bot_token(session: Session, bot_token: str) -> BotToken:
        hashed_bot_token = cryptographic_hash(bot_token)
        entity = session.query(BotToken).filter_by(hashed_token=hashed_bot_token).first()
        if entity is not None:
            return entity
        bot_token_entity = BotToken(hashed_token=hashed_bot_token)
        session.add(bot_token_entity)
        session.commit()
        session.refresh(bot_token_entity)
        return bot_token_entity

    @staticmethod
    def get(session: Session, entity_id: int):
        return session.query(Image).get(entity_id)

    @staticmethod
    def get_all(session: Session) -> [Image]:
        return session.query(Image).order_by(Image.created.desc()).all()

    @staticmethod
    def add_all(session: Session, entities: [Image]):
        session.add_all(entities)

    @staticmethod
    def add(session: Session, image: Image):
        session.add(image)
        session.commit()
        session.refresh(image)
        return image

    @staticmethod
    def get_random(session: Session, page_size: int = None) -> Image or [Image]:
        query = session.query(Image).order_by(func.random()).limit(page_size)
        if page_size is None:
            return query.first()
        else:
            return query.all()

    @staticmethod
    def find_by_image_hash(session: Session, image_hash: str) -> Image or None:
        return session.query(Image).filter_by(image_hash=image_hash).first()

    def find_by_url(self, session: Session, url: str) -> [Image]:
        return session.query(Image).filter_by(url=url).all()

    @staticmethod
    def find_by_telegram_file_id(session: Session, telegram_file_id: str) -> [Image]:
        return session.query(Image).filter(Image.telegram_file_ids.any(id=telegram_file_id)).first()

    @staticmethod
    def find_by_text(session: Session, text: str = None, limit: int = None, offset: int = None) -> [Image]:
        if limit is None:
            limit = 16

        words = text.split(" ")

        filters = list(map(lambda word: Image.text.ilike("%{}%".format(word)), words))
        return session.query(Image).filter(and_(*filters)).limit(limit).offset(offset).all()

    def find_all_non_optimal(self, session: Session, target_quality: int, limit: int = None) -> [Image]:
        never_analysed = session.query(Image.id).filter(Image.analyser_quality.is_(None)).order_by(
            func.length(Image.text) > 0,
            Image.created).all()

        improvement_possible = session.query(Image.id).filter(
            and_(Image.analyser_quality.isnot(None),
                 Image.analyser_quality < target_quality)
        ).order_by(
            func.length(Image.text) > 0,
            Image.analyser_quality,
            Image.created).all()

        return never_analysed + improvement_possible

    @staticmethod
    def get_not_uploaded_image_ids(session: Session, bot_token: str) -> List[int]:
        hashed_bot_token = cryptographic_hash(bot_token)
        image_ids = session.query(Image.id).all()
        bot_token_entity = session.query(BotToken).filter_by(hashed_token=hashed_bot_token).first()
        if bot_token_entity is None:
            return []
        uploaded_image_ids = set(map(lambda x: x.image_id, bot_token_entity.telegram_file_ids))

        x = image_ids
        y = uploaded_image_ids
        remaining = Counter(y)

        # out would be the full substraction
        out = []
        for val in x:
            if remaining[val]:
                remaining[val] -= 1
            else:
                out.append(val)

        # TODO: this still takes about 30 seconds and shifts part of the load to the client,
        #  but its the best we have now
        return out

    @staticmethod
    def count(session: Session) -> int:
        return session.query(func.count(Image.id)).scalar()

    @staticmethod
    def update(session: Session, image: Image) -> None:
        session.merge(image)

    @staticmethod
    def count_items_this_month(session: Session, analyser: str) -> int:
        return session.query(Image).filter(Image.analyser == analyser).filter(
            Image.created > (time.time() - 60 * 60 * 24 * 31)).count()

    @staticmethod
    def delete(session: Session, entity_id: int) -> None:
        session.query(Image).filter_by(id=entity_id).delete()

    def clear(self) -> None:
        raise NotImplementedError()

    @staticmethod
    def count_items_with_telegram_upload(session: Session, bot_token: str) -> int:
        hashed_bot_token = cryptographic_hash(bot_token)
        return session.query(Image).filter(
            and_(Image.telegram_file_ids.any(
                TelegramFileId.bot_tokens.any(BotToken.hashed_token.in_([hashed_bot_token]))))).count()

    @staticmethod
    def count_items_by_analyser(session: Session, analyser_id: str) -> int:
        return session.query(Image).filter(Image.analyser == analyser_id).count()

    @staticmethod
    def count_items_with_text(session: Session) -> int:
        return session.query(Image).filter(func.length(Image.text) > 0).count()

    @staticmethod
    def count_items_with_image_data(session: Session) -> int:
        return session.query(Image).filter(Image.image_hash.isnot(None)).count()
