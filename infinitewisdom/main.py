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

from container_app_conf.formatter.toml import TomlFormatter

parent_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))
sys.path.append(parent_dir)

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    from prometheus_client import start_http_server
    from infinitewisdom.analysis.googlevision import GoogleVision
    from infinitewisdom.analysis.microsoftazure import AzureComputerVision
    from infinitewisdom.analysis.tesseract import Tesseract
    from infinitewisdom.analysis.worker import AnalysisWorker
    from infinitewisdom.bot import InfiniteWisdomBot
    from infinitewisdom.config.config import AppConfig
    from infinitewisdom.crawler import Crawler
    from infinitewisdom.persistence import ImageDataPersistence
    from infinitewisdom.uploader import TelegramUploader

    config = AppConfig()

    log_level = logging._nameToLevel.get(str(config.LOG_LEVEL.value).upper(), config.LOG_LEVEL.default)
    logging.getLogger("infinitewisdom").setLevel(log_level)

    LOGGER.debug("Config:\n{}".format(config.print(TomlFormatter())))

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
    telegram_uploader = TelegramUploader(config, persistence, wisdom_bot._updater.bot)
    analysis_worker = AnalysisWorker(config, persistence, image_analysers)
    crawler = Crawler(config, persistence, telegram_uploader, image_analysers, analysis_worker)

    crawler.start()
    analysis_worker.start()
    telegram_uploader.start()

    wisdom_bot.start()
