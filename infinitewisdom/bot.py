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
from io import BytesIO

from prometheus_client import start_http_server
from telegram import InlineQueryResultPhoto, ChatAction, Bot, Update, InlineQueryResultCachedPhoto
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater, ChosenInlineResultHandler

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.analysis.googlevision import GoogleVision
from infinitewisdom.analysis.tesseract import Tesseract
from infinitewisdom.analysis.worker import AnalysisWorker
from infinitewisdom.config import Config
from infinitewisdom.const import PERSISTENCE_TYPE_PICKLE, PERSISTENCE_TYPE_SQL
from infinitewisdom.crawler import Crawler
from infinitewisdom.persistence import Entity, ImageDataPersistence
from infinitewisdom.persistence.pickle import PicklePersistence
from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence
from infinitewisdom.stats import INSPIRE_TIME, INLINE_TIME, START_TIME, CHOSEN_INLINE_RESULTS
from infinitewisdom.util import download_image_bytes

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class InfiniteWisdomBot:
    """
    The main entry class of the InfiniteWisdom telegram bot
    """

    def __init__(self, config: Config, persistence: ImageDataPersistence, image_analysers: [ImageAnalyser]):
        """
        Creates an instance.
        :param config: configuration object
        """
        self._config = config
        self._persistence = persistence
        self._image_analysers = image_analysers

        self._updater = Updater(token=self._config.TELEGRAM_BOT_TOKEN.value)

        self._dispatcher = self._updater.dispatcher
        self._dispatcher.add_handler(CommandHandler('start', self._start_callback))
        self._dispatcher.add_handler(InlineQueryHandler(self._inline_query_callback))
        self._dispatcher.add_handler(MessageHandler(Filters.command, self._command_callback))
        self._dispatcher.add_handler(ChosenInlineResultHandler(self._inline_result_chosen_callback))

    def start(self):
        """
        Starts up the bot.
        This means filling the url pool and listening for messages.
        """
        self._updater.start_polling()

    def stop(self):
        """
        Shuts down the bot.
        """
        self._updater.stop()

    @START_TIME.time()
    def _start_callback(self, bot: Bot, update: Update) -> None:
        """
        Welcomes a new user with an example image and a greeting message
        :param bot: the bot
        :param update: the chat update object
        """
        self._send_random_quote(bot, update)
        bot.send_message(chat_id=update.message.chat_id,
                         text=self._config.TELEGRAM_GREETING_MESSAGE.value)

    def _command_callback(self, bot: Bot, update: Update) -> None:
        """
        Handles commands send by a user
        :param bot: the bot
        :param update: the chat update object
        """
        self._send_random_quote(bot, update)

    @INSPIRE_TIME.time()
    def _send_random_quote(self, bot: Bot, update: Update) -> None:
        """
        Sends a quote from the pool to the requesting chat
        :param bot: the bot
        :param update: the chat update object
        """
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        entity = self._persistence.get_random()
        LOGGER.debug('Got image URL from the pool: {}'.format(entity.url))

        if entity.telegram_file_id is None:
            image_bytes = download_image_bytes(entity.url)
            file_id = self._send_photo(bot=bot, chat_id=update.message.chat_id, image_data=image_bytes)
            entity.telegram_file_id = file_id
            self._persistence.update(entity)
        else:
            self._send_photo(bot=bot, chat_id=update.message.chat_id, file_id=entity.telegram_file_id)

    @staticmethod
    def _send_photo(bot: Bot, chat_id: str, file_id: int or None = None, image_data: bytes or None = None) -> int:
        """
        Sends a photo to the given chat
        :param bot: the bot
        :param chat_id: the chat id to send the image to
        :param image_data: the image data
        :return: telegram message id
        """
        if image_data is not None:
            image_bytes_io = BytesIO(image_data)
            image_bytes_io.name = 'inspireme.jpeg'
            photo = image_bytes_io
        elif file_id is not None:
            photo = file_id
        else:
            raise ValueError("At least one of file_id and image_data has to be provided!")

        message = bot.send_photo(chat_id=chat_id, photo=photo)
        return message.photo[-1].file_id

    @INLINE_TIME.time()
    def _inline_query_callback(self, bot: Bot, update: Update) -> None:
        """
        Responds to an inline client request with a list of 16 randomly chosen images
        :param bot: the bot
        :param update: the chat update object
        """
        LOGGER.debug('Inline query')

        query = update.inline_query.query
        offset = update.inline_query.offset
        if not offset:
            offset = 0
        else:
            offset = int(offset)
        badge_size = self._config.TELEGRAM_INLINE_BADGE_SIZE.value

        if len(query) > 0:
            entities = self._persistence.find_by_text(query, badge_size, offset)
        else:
            entities = self._persistence.get_random(page_size=badge_size)

        results = list(map(lambda x: self._entity_to_inline_query_result(x), entities))
        LOGGER.debug('Inline query "{}": {}+{} results'.format(query, len(results), offset))

        if len(results) > 0:
            new_offset = offset + badge_size
        else:
            new_offset = ''

        update.inline_query.answer(
            results,
            next_offset=new_offset
        )

    @staticmethod
    def _inline_result_chosen_callback(bot: Bot, update: Update):
        CHOSEN_INLINE_RESULTS.inc()

    @staticmethod
    def _entity_to_inline_query_result(entity: Entity):
        """
        Creates a telegram inline query result object for the given entity
        :param entity: the entity to use
        :return: inline result object
        """
        if entity.telegram_file_id is not None:
            return InlineQueryResultCachedPhoto(
                id=entity.url,
                photo_file_id=str(entity.telegram_file_id),
            )
        else:
            return InlineQueryResultPhoto(
                id=entity.url,
                photo_url=entity.url,
                thumb_url=entity.url,
                photo_height=50,
                photo_width=50
            )


if __name__ == '__main__':
    config = Config()

    persistence = None
    if config.PERSISTENCE_TYPE.value == PERSISTENCE_TYPE_PICKLE:
        persistence = PicklePersistence(config.PICKLE_PERSISTENCE_PATH.value)
    elif config.PERSISTENCE_TYPE.value == PERSISTENCE_TYPE_SQL:
        persistence = SQLAlchemyPersistence(config.SQL_PERSISTENCE_URL.value)
    else:
        raise AssertionError("No persistence was instantiated but is required for execution")

    image_analysers = []
    if config.IMAGE_ANALYSIS_TESSERACT_ENABLED.value:
        image_analysers.append(Tesseract())
    if config.IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED.value:
        auth_file = config.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value
        capacity = config.IMAGE_ANALYSIS_GOOGLE_VISION_CAPACITY.value
        image_analysers.append(GoogleVision(auth_file, capacity))

    # start prometheus server
    start_http_server(8000)

    wisdom_bot = InfiniteWisdomBot(config, persistence, image_analysers)
    crawler = Crawler(config, persistence, image_analysers)
    analysis_worker = AnalysisWorker(config, persistence, image_analysers)

    wisdom_bot.start()
    crawler.start()
    analysis_worker.start()
