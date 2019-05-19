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
import random
from collections import deque
from io import BytesIO
from time import sleep

import requests
from prometheus_client import start_http_server, Gauge, Summary
from telegram import InlineQueryResultPhoto, ChatAction, Bot, Update
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater

from const import ENV_PARAM_BOT_TOKEN

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

POOL_SIZE = Gauge('pool_size', 'Size of the URL pool')
START_TIME = Summary('start_processing_seconds', 'Time spent in the /start handler')
INSPIRE_TIME = Summary('inspire_processing_seconds', 'Time spent in the /inspire handler')
INLINE_TIME = Summary('inline_processing_seconds', 'Time spent in the inline query handler')

url_pool = deque(maxlen=10000)


def load_config() -> dict:
    """
    Loads the configuration from environment variables
    :return: configuration
    """
    return {
        ENV_PARAM_BOT_TOKEN: os.environ.get(ENV_PARAM_BOT_TOKEN)
    }


def add_image_url_to_pool() -> str:
    """
    Requests a new image url and adds it to the pool
    :return: the added url
    """
    url = fetch_generated_image_url()
    url_pool.append(url)
    POOL_SIZE.set(len(url_pool))
    LOGGER.debug('Added image URL to the pool (length: {}): {}'.format(len(url_pool), url))
    return url


def fetch_generated_image_url() -> str:
    """
    Requests the image api to generate a new image url
    :return: the image url
    """
    url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'})
    url_page.raise_for_status()
    return url_page.text


def get_image_url() -> str:
    """
    Pops the oldest image url from the pool
    :return: image url
    """
    url = url_pool.popleft()
    POOL_SIZE.set(len(url_pool))
    LOGGER.debug('Got image URL from the pool: {}'.format(url))
    return url


def download_image_bytes(url: str) -> bytes:
    """
    Downloads the image from the given url
    :return: the downloaded image
    """
    image = requests.get(url)
    image.raise_for_status()
    LOGGER.debug('Fetched image from: {}'.format(url))
    return image.content

@START_TIME.time()
def start(bot: Bot, update: Update) -> None:
    """
    Welcomes a new user with an example image and a greeting message
    :param bot:
    :param update:
    :return:
    """
    send_random_quote(bot, update)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.')


@INSPIRE_TIME.time()
def send_random_quote(bot: Bot, update: Update) -> None:
    """
    Sends a quote from the pool to the requesting chat
    :param bot: the bot
    :param update: the chat update object
    """
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    image_url = get_image_url()
    image_bytes = download_image_bytes(image_url)
    send_photo(bot=bot, chat_id=update.message.chat_id, image_data=image_bytes)


def send_photo(bot: Bot, chat_id: str, image_data: bytes) -> None:
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
def inlinequery(bot: Bot, update: Update) -> None:
    """
    Responds to an inline client request with a list of 16 randomly chosen images
    :param bot: the bot
    :param update: the chat update object
    """
    LOGGER.debug('Inline query')
    query = update.inline_query.query
    offset = update.inline_query.offset
    results = []
    for url in random.sample(url_pool, k=16):
        results.append(InlineQueryResultPhoto(
            id=url,
            photo_url=url,
            thumb_url=url,
            photo_height=50,
            photo_width=50
        ))
    LOGGER.debug('Inline query "{}": {}+{} results'.format(query, len(results), offset))

    if not offset:
        offset = 0
    new_offset = int(offset) + 16
    update.inline_query.answer(
        results,
        next_offset=new_offset
    )

def add_quotes(count: int = 300) -> None:
    """
    Adds the given amount of image url's to the pool, sleeping between ever single
    one of them. This method is blocking so it should be called from a background thread.
    :param count: amount of image url's to query
    """
    for _ in range(count):
        add_image_url_to_pool()
        sleep(1)


def add_quotes_job(bot: Bot, update: Update) -> None:
    add_quotes(count=300)


if __name__ == '__main__':
    config = load_config()

    add_quotes(count=16)
    updater = Updater(token=config[ENV_PARAM_BOT_TOKEN])
    dispatcher = updater.dispatcher

    start_http_server(8000)

    queue = updater.job_queue
    queue.run_repeating(add_quotes_job, interval=600, first=0)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    dispatcher.add_handler(MessageHandler(Filters.command, send_random_quote))

    updater.start_polling()
