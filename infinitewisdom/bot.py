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
import sys

parent_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))
sys.path.append(parent_dir)

from infinitewisdom.config.config import Config
from prometheus_client import start_http_server
from telegram import InlineQueryResultPhoto, ChatAction, Bot, Update, InlineQueryResultCachedPhoto
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater, ChosenInlineResultHandler

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.analysis.googlevision import GoogleVision
from infinitewisdom.analysis.microsoftazure import AzureComputerVision
from infinitewisdom.analysis.tesseract import Tesseract
from infinitewisdom.analysis.worker import AnalysisWorker
from infinitewisdom.crawler import Crawler
from infinitewisdom.persistence import Entity, ImageDataPersistence
from infinitewisdom.stats import INSPIRE_TIME, INLINE_TIME, START_TIME, CHOSEN_INLINE_RESULTS
from infinitewisdom.uploader import TelegramUploader
from infinitewisdom.util import _send_photo, _send_message

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
        _send_message(bot=bot, chat_id=update.message.chat_id,
                      message=self._config.TELEGRAM_GREETING_MESSAGE.value)

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
        chat_id = update.message.chat_id
        bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        entity = self._persistence.get_random()
        LOGGER.debug('Got image URL from the pool: {}'.format(entity.url))

        caption = None
        if self._config.TELEGRAM_CAPTION_IMAGES_WITH_TEXT.value:
            caption = entity.text

        if entity.telegram_file_id is not None:
            _send_photo(bot=bot, chat_id=chat_id, file_id=entity.telegram_file_id, caption=caption)
            return

        image_bytes = self._persistence._image_data_store.get(entity.image_hash)
        file_id = _send_photo(bot=bot, chat_id=chat_id, image_data=image_bytes, caption=caption)
        entity.telegram_file_id = file_id
        self._persistence.update(entity, image_bytes)

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

    persistence = ImageDataPersistence(config)

    image_analysers = []
    if config.IMAGE_ANALYSIS_TESSERACT_ENABLED.value:
        image_analysers.append(Tesseract())
    if config.IMAGE_ANALYSIS_GOOGLE_VISION_ENABLED.value:
        auth_file = config.IMAGE_ANALYSIS_GOOGLE_VISION_AUTH_FILE.value
        capacity = config.IMAGE_ANALYSIS_GOOGLE_VISION_CAPACITY.value
        image_analysers.append(GoogleVision(auth_file, capacity))
    if config.IMAGE_ANALYSIS_MICROSOFT_AZURE_ENABLED.value:
        key = config.IMAGE_ANALYSIS_MICROSOFT_AZURE_SUBSCRIPTION_KEY.value
        region = config.IMAGE_ANALYSIS_MICROSOFT_AZURE_REGION.value
        capacity = config.IMAGE_ANALYSIS_MICROSOFT_AZURE_CAPACITY.value
        image_analysers.append(AzureComputerVision(key, region, capacity))

    # start prometheus server
    start_http_server(8000)

    wisdom_bot = InfiniteWisdomBot(config, persistence, image_analysers)
    crawler = Crawler(config, persistence, image_analysers)
    analysis_worker = AnalysisWorker(config, persistence, image_analysers)
    telegram_uploader = TelegramUploader(config, persistence, wisdom_bot._updater.bot)

    wisdom_bot.start()
    crawler.start()
    analysis_worker.start()

    telegram_uploader.start()
