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
from io import BytesIO
from collections import deque
from time import sleep

import requests
from PIL import Image
from prometheus_client import start_http_server, Gauge, Summary
from telegram import InlineQueryResultPhoto, ChatAction
from telegram.ext import CommandHandler, Filters, InlineQueryHandler, MessageHandler, Updater

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

POOL_SIZE = Gauge('pool_size', 'Size of the URL pool')
START_TIME = Summary('start_processing_seconds', 'Time spent in the /start handler')
INSPIRE_TIME = Summary('inspire_processing_seconds', 'Time spent in the /inspire handler')
INLINE_TIME = Summary('inline_processing_seconds', 'Time spent in the inline query handler')

TOKEN = os.environ.get('BOT_TOKEN')

url_pool = deque(maxlen=10000)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

def add_image_url_to_pool() -> str:
    url_page = requests.get('https://inspirobot.me/api', params={'generate': 'true'})
    url_page.raise_for_status()
    url = url_page.text
    url_pool.append(url)
    POOL_SIZE.set(len(url_pool))
    LOGGER.debug('Added image URL to the pool (length: {}): {}'.format(len(url_pool), url))
    return url

def get_image_url() -> str:
    url = url_pool.popleft()
    POOL_SIZE.set(len(url_pool))
    LOGGER.debug('Got image URL from the pool: {}'.format(url))
    return url

def get_image():
    url = get_image_url()
    image = requests.get(url)
    image.raise_for_status()
    LOGGER.debug('Fetched image from: {}'.format(url))
    return Image.open(BytesIO(image.content))

@START_TIME.time()
def start(bot, update):
    send_random_quote(bot, update)
    bot.send_message(chat_id=update.message.chat_id, text='Send /inspire for more inspiration :) Or use @InfiniteWisdomBot in a group chat and select one of the suggestions.')

@INSPIRE_TIME.time()
def send_random_quote(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    image = get_image()
    bio = BytesIO()
    bio.name = 'inspireme.jpeg'
    image.save(bio, 'JPEG')
    bio.seek(0)
    bot.send_photo(chat_id=update.message.chat_id, photo=bio)

@INLINE_TIME.time()
def inlinequery(bot, update):
    LOGGER.debug('Inline query')
    results = []
    for u in random.sample(url_pool, k=16):
        results.append(InlineQueryResultPhoto(
            id=u,
            photo_url=u,
            thumb_url=u,
            photo_height=50,
            photo_width=50
        ))
    LOGGER.debug('Inline results: {}'.format(len(results)))
    update.inline_query.answer(results)

def add_quotes(count=300):
    for _ in range(count):
        add_image_url_to_pool()
        sleep(1)

def add_quotes_job(bot, update):
    add_quotes(count=300)


start_http_server(8000)

add_quotes(count=16)

queue = updater.job_queue
queue.run_repeating(add_quotes_job, interval=600, first=0)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(InlineQueryHandler(inlinequery))
dispatcher.add_handler(MessageHandler(Filters.command, send_random_quote))

updater.start_polling()
