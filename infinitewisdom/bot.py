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

from infinitewisdom.const import SUPPORTED_REPLY_COMMANDS, COMMAND_START, REPLY_COMMAND_DELETE, REPLY_COMMAND_TEXT, \
    IMAGE_ANALYSIS_TYPE_HUMAN

parent_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))
sys.path.append(parent_dir)

from infinitewisdom.config.config import Config
from prometheus_client import start_http_server
from telegram import InlineQueryResultPhoto, ChatAction, Update, InlineQueryResultCachedPhoto, ParseMode
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater, \
    ChosenInlineResultHandler, CallbackContext

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.analysis.googlevision import GoogleVision
from infinitewisdom.analysis.microsoftazure import AzureComputerVision
from infinitewisdom.analysis.tesseract import Tesseract
from infinitewisdom.analysis.worker import AnalysisWorker
from infinitewisdom.crawler import Crawler
from infinitewisdom.persistence import Entity, ImageDataPersistence
from infinitewisdom.stats import INSPIRE_TIME, INLINE_TIME, START_TIME, CHOSEN_INLINE_RESULTS, REPLY_TIME
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

        self._updater = Updater(token=self._config.TELEGRAM_BOT_TOKEN.value, use_context=True)
        LOGGER.debug("Using bot id '{}' ({})".format(self._updater.bot.id, self._updater.bot.name))

        self._dispatcher = self._updater.dispatcher
        self._dispatcher.add_handler(
            CommandHandler(COMMAND_START,
                           filters=(~ Filters.reply) & (~ Filters.forwarded),
                           callback=self._start_callback))

        self._dispatcher.add_handler(
            MessageHandler(
                filters=Filters.command & (~ Filters.reply) & (~ Filters.forwarded),
                callback=self._command_callback))

        self._dispatcher.add_handler(
            MessageHandler(
                filters=Filters.command & Filters.reply & (~ Filters.forwarded),
                callback=self._reply_command_callback))

        self._dispatcher.add_handler(
            MessageHandler(
                filters=Filters.reply & (~ Filters.forwarded),
                callback=self._reply_callback))

        self._dispatcher.add_handler(InlineQueryHandler(self._inline_query_callback))
        self._dispatcher.add_handler(ChosenInlineResultHandler(self._inline_result_chosen_callback))

    @property
    def bot(self):
        return self._updater.bot

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
    def _start_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Welcomes a new user with an example image and a greeting message
        :param update: the chat update object
        :param context: telegram context
        """
        bot = context.bot
        self._send_random_quote(update, context)
        greeting_message = self._config.TELEGRAM_GREETING_MESSAGE.value
        if greeting_message is not None and len(greeting_message) > 0:
            _send_message(bot=bot, chat_id=update.message.chat_id, message=greeting_message)

    def _command_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Handles commands send by a user
        :param update: the chat update object
        :param context: telegram context
        """
        command, args = self._parse_command(update.message.text)
        self._send_random_quote(update, context)

    @INSPIRE_TIME.time()
    def _send_random_quote(self, update: Update, context: CallbackContext) -> None:
        """
        Sends a quote from the pool to the requesting chat
        :param update: the chat update object
        :param context: telegram context
        """
        bot = context.bot
        chat_id = update.message.chat_id
        bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        entity = self._persistence.get_random()
        LOGGER.debug("Sending random quote '{}' to chat id: {}".format(entity.image_hash, chat_id))

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

    def _reply_command_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Handles commands send as a reply to another message
        :param update:
        :param context:
        :return:
        """
        bot = context.bot
        message = update.effective_message
        from_user = message.from_user
        chat_id = message.chat_id
        text = message.text
        reply_to_message = message.reply_to_message
        is_edit = hasattr(message, 'edited_message') and message.edited_message is not None

        command, args = self._parse_command(text)

        if command not in SUPPORTED_REPLY_COMMANDS:
            _send_message(bot, chat_id, "Unsupported command: `/{}`".format(command), parse_mode=ParseMode.MARKDOWN)
            return

        if reply_to_message.effective_attachment is None:
            _send_message(bot, chat_id, "You must directly reply to an image send by this bot to use reply commands.")
            return

        reply_image = next(iter(sorted(reply_to_message.effective_attachment, key=lambda x: x.file_size, reverse=True)),
                           None)
        telegram_file_id = reply_image.file_id

        entity = self._persistence.find_by_telegram_file_id(telegram_file_id)

        LOGGER.debug(
            "Received reply from user '{}' in chat '{}' to image_hash '{}' with message: {}".format(from_user.username,
                                                                                                    chat_id,
                                                                                                    entity.image_hash,
                                                                                                    text))

        if command == REPLY_COMMAND_DELETE:
            if is_edit:
                LOGGER.debug("Ignoring edited delete command")
                return

            try:
                # self._persistence.delete(entity)
                _send_message(bot, chat_id,
                              "Deleted referenced image from persistence (Hash: {})".format(entity.image_hash))
            except Exception as e:
                _send_message(bot, chat_id, "Error deleting image: ```{}```".format(e), parse_mode=ParseMode.MARKDOWN)

        elif command == REPLY_COMMAND_TEXT:
            try:
                entity.analyser = IMAGE_ANALYSIS_TYPE_HUMAN
                entity.analyser_quality = 1.0
                entity.text = args
                self._persistence.update(entity)
                _send_message(bot, chat_id,
                              "Updated text for referenced image to '{}' (Hash: {})".format(entity.text,
                                                                                            entity.image_hash))
            except Exception as e:
                _send_message(bot, chat_id, "Error updating image: ```{}```".format(e), parse_mode=ParseMode.MARKDOWN)

    @REPLY_TIME.time()
    def _reply_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Handles user reply messages
        :param update: the chat update object
        :param context: telegram context
        """
        pass

    @INLINE_TIME.time()
    def _inline_query_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Responds to an inline client request with a list of 16 randomly chosen images
        :param update: the chat update object
        :param context: telegram context
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
    def _inline_result_chosen_callback(update: Update, context: CallbackContext):
        """
        Called when an inline result is chosen by a user
        :param update: the chat update object
        :param context: telegram context
        """
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

    @staticmethod
    def _parse_command(text: str) -> (str, [str]):
        """
        Parses the given message to a command and its arguments
        :param text: the text to parse
        :return: the command and its argument list
        """
        if text is None or len(text) <= 0:
            return None, [0]

        if " " not in text:
            return text[1:], None
        else:
            command, rest = text.split(" ", 1)
            return command[1:], rest


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
    start_http_server(config.STATS_PORT.value)

    wisdom_bot = InfiniteWisdomBot(config, persistence, image_analysers)
    crawler = Crawler(config, persistence, image_analysers)
    analysis_worker = AnalysisWorker(config, persistence, image_analysers)
    telegram_uploader = TelegramUploader(config, persistence, wisdom_bot._updater.bot)

    wisdom_bot.start()
    crawler.start()
    analysis_worker.start()

    telegram_uploader.start()
