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
from time import sleep

import requests
from prometheus_client import start_http_server
from telegram import InlineQueryResultPhoto, ChatAction, Bot, Update
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater

from config import Config
from persistence import LocalPersistence
from stats import INSPIRE_TIME, INLINE_TIME, START_TIME

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class InfiniteWisdomBot:
    """
    The main entry class of the InfiniteWisdom telegram bot
    """

    def __init__(self):
        self._config = Config()
        self._persistence = LocalPersistence()
        self._updater = Updater(token=self._config.BOT_TOKEN)

        self._dispatcher = self._updater.dispatcher
        self._dispatcher.add_handler(CommandHandler('start', self._start_callback))
        self._dispatcher.add_handler(InlineQueryHandler(self._inline_query_callback))
        self._dispatcher.add_handler(MessageHandler(Filters.command, self._command_callback))

    def start(self):
        """
        Starts up the bot.
        This means filling the url pool and listening for messages.
        """
        if self._persistence.count() < 16:
            self._add_quotes(count=16)

        queue = self._updater.job_queue
        queue.run_repeating(self._add_quotes_job, interval=600, first=0)

        self._updater.start_polling()

    def stop(self):
        """
        Shuts down the bot.
        """
        self._updater.stop()

    def add_image_url_to_pool(self) -> str:
        """
        Requests a new image url and adds it to the pool
        :return: the added url
        """
        url = self._fetch_generated_image_url()
        self._persistence.add(url)
        LOGGER.debug('Added image URL to the pool (length: {}): {}'.format(self._persistence.count(), url))
        return url

    @staticmethod
    def _fetch_generated_image_url() -> str:
        """
        Requests the image api to generate a new image url
        :return: the image url
        """
        url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'})
        url_page.raise_for_status()
        return url_page.text

    def _get_image_url(self) -> str:
        """
        Returns a random image url from the persistence
        :return: image url
        """
        entity = self._persistence.get_random()
        LOGGER.debug('Got image URL from the pool: {}'.format(entity.url))
        return entity.url

    @staticmethod
    def _download_image_bytes(url: str) -> bytes:
        """
        Downloads the image from the given url
        :return: the downloaded image
        """
        image = requests.get(url)
        image.raise_for_status()
        LOGGER.debug('Fetched image from: {}'.format(url))
        return image.content

    @START_TIME.time()
    def _start_callback(self, bot: Bot, update: Update) -> None:
        """
        Welcomes a new user with an example image and a greeting message
        :param bot: the bot
        :param update: the chat update object
        """
        self._send_random_quote(bot, update)
        bot.send_message(chat_id=update.message.chat_id,
                         text=self._config.GREETING_MESSAGE)

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
        image_url = self._get_image_url()
        image_bytes = self._download_image_bytes(image_url)
        self._send_photo(bot=bot, chat_id=update.message.chat_id, image_data=image_bytes)

    @staticmethod
    def _send_photo(bot: Bot, chat_id: str, image_data: bytes) -> None:
        """
        Sends a photo to the given chat
        :param bot: the bot
        :param chat_id: the chat id to send the image to
        :param image_data: the image data
        """
        image_bytes_io = BytesIO(image_data)
        image_bytes_io.name = 'inspireme.jpeg'
        bot.send_photo(chat_id=chat_id, photo=image_bytes_io)

    @INLINE_TIME.time()
    def _inline_query_callback(self, bot: Bot, update: Update) -> None:
        """
        Responds to an inline client request with a list of 16 randomly chosen images
        :param bot: the bot
        :param update: the chat update object
        """
        LOGGER.debug('Inline query')

        random_entities = self._persistence.get_random(sample_size=16)
        results = list(map(lambda x: InlineQueryResultPhoto(
            id=x.url,
            photo_url=x.url,
            thumb_url=x.url,
            photo_height=50,
            photo_width=50
        ), random_entities))

        LOGGER.debug('Inline results: {}'.format(len(results)))
        update.inline_query.answer(results)

    def _add_quotes(self, count: int = 300) -> None:
        """
        Adds the given amount of image url's to the pool, sleeping between ever single
        one of them. This method is blocking so it should be called from a background thread.
        :param count: amount of image url's to query
        """
        for _ in range(count):
            self.add_image_url_to_pool()
            sleep(self._config.IMAGE_POLLING_TIMEOUT)

    def _add_quotes_job(self, bot: Bot, update: Update) -> None:
        self._add_quotes(count=300)


if __name__ == '__main__':
    start_http_server(8000)
    wisdom_bot = InfiniteWisdomBot()
    wisdom_bot.start()
