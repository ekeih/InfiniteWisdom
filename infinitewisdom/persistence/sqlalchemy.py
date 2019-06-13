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

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from infinitewisdom.persistence import ImageDataPersistence, Entity

Base = declarative_base()


class Image(Base, Entity):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)

    url = Column(String)
    text = Column(String)
    analyser = Column(String)
    analyser_quality = Column(Float)
    created = Column(String)
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
