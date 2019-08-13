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
import hashlib
import logging
import os
from io import BytesIO

import requests
from emoji import emojize
from telegram import Bot

from infinitewisdom.analysis import ImageAnalyser
from infinitewisdom.const import TELEGRAM_CAPTION_LENGTH_LIMIT

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def download_image_bytes(url: str) -> bytes:
    """
    Downloads the image from the given url
    :return: the downloaded image
    """
    image = requests.get(url)
    image.raise_for_status()
    return image.content


def create_hash(data: bytes) -> str:
    """
    Creates a hash of the given bytes
    :param data: data to hash
    :return: hash
    """
    return hashlib.md5(data).hexdigest()


def select_best_available_analyser(analysers: [ImageAnalyser], persistence) -> ImageAnalyser or None:
    """
    Selects the best available analyser based on it's quality and remaining capacity
    :param analysers: the analysers to choose from
    :param persistence: currently in use persistence
    :return: analyser or None
    """

    if len(analysers) == 1:
        return analysers[0]

    def remaining_capacity(analyser) -> int:
        """
        Calculates the remaining capacity of an analyser
        :param analyser: the analyser to check
        :return: the remaining capacity of the analyser
        """
        count = persistence.count_items_this_month(analyser.get_identifier())
        remaining = analyser.get_monthly_capacity() - count
        return remaining

    available = list(filter(lambda x: remaining_capacity(x) > 0, analysers))
    if len(available) <= 0:
        return None
    else:
        return sorted(available, key=lambda x: (-x.get_quality(), -remaining_capacity(x)))[0]


def parse_telegram_command(text: str) -> (str, [str]):
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


def send_photo(bot: Bot, chat_id: str, file_id: int or None = None, image_data: bytes or None = None,
               caption: str = None) -> int:
    """
    Sends a photo to the given chat
    :param bot: the bot
    :param chat_id: the chat id to send the image to
    :param file_id: the telegram file id of the already uploaded image
    :param image_data: the image data
    :param caption: an optional image caption
    :return: telegram image file id
    """
    if image_data is not None:
        image_bytes_io = BytesIO(image_data)
        image_bytes_io.name = 'inspireme.jpeg'
        photo = image_bytes_io
    elif file_id is not None:
        photo = file_id
    else:
        raise ValueError("At least one of file_id and image_data has to be provided!")

    if caption is not None:
        caption = _format_caption(caption)

    message = bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
    return message.photo[-1].file_id


def format_for_single_line_log(text: str) -> str:
    """
    Formats a text for log
    :param text:
    :return:
    """
    return " ".join(text.split())


def _format_caption(text: str) -> str or None:
    if text is None:
        return None

    # remove empty lines
    text = os.linesep.join([s for s in text.splitlines() if s.strip()])
    # limit to 200 characters (telegram api limitation)
    if len(text) > TELEGRAM_CAPTION_LENGTH_LIMIT:
        text = text[:197] + "…"

    return text


def send_message(bot: Bot, chat_id: str, message: str, parse_mode: str = None, reply_to: int = None):
    """
    Sends a text message to the given chat
    :param bot: the bot
    :param chat_id: the chat id to send the message to
    :param message: the message to chat (may contain emoji aliases)
    :param parse_mode: specify whether to parse the text as markdown or HTML
    :param reply_to: the message id to reply to
    """
    emojized_text = emojize(message, use_aliases=True)
    bot.send_message(chat_id=chat_id, parse_mode=parse_mode, text=emojized_text, reply_to_message_id=reply_to)
