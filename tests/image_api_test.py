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

import os
import unittest
from unittest import mock

from infinitewisdom.const import ENV_PARAM_BOT_TOKEN


class ImageApiTests(unittest.TestCase):
    """
    Tests for the image api
    """

    @mock.patch.dict(os.environ, {
        ENV_PARAM_BOT_TOKEN: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    })
    def test_retrieve_new_image(self):
        from infinitewisdom.bot import InfiniteWisdomBot
        url = InfiniteWisdomBot._fetch_generated_image_url()
        self.assertRegex(url, r'https://generated\.inspirobot\.me/\w/\w+\.jpg')
