import os
import unittest
from unittest import mock

from const import ENV_PARAM_BOT_TOKEN


class ImageApiTests(unittest.TestCase):

    @mock.patch.dict(os.environ, {
        ENV_PARAM_BOT_TOKEN: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    })
    def test_retrieve_new_image(self):
        from bot import fetch_generated_image_url

        url = fetch_generated_image_url()
        self.assertRegexpMatches(url, r'https://generated\.inspirobot\.me/\w/\w+\.jpg')
