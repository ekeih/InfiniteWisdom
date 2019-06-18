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

from prometheus_client import Gauge, Counter, Summary

POOL_SIZE = Gauge('pool_size', 'Size of the URL pool')
TELEGRAM_ENTITIES_COUNT = Gauge('telegram_entities_count',
                                'Number of items that have been uploaded to telegram servers')
ENTITIES_WITH_IMAGE_DATA_COUNT = Gauge('entities_with_image_data_count',
                                       'Number of entites that have image data')
IMAGE_ANALYSIS_TYPE_COUNT = Gauge('image_analysis_type_count',
                                  'Number of entities that have been analysed by a specific analyser',
                                  ['type'])
IMAGE_ANALYSIS_HAS_TEXT_COUNT = Gauge('image_analysis_has_text_count',
                                      'Number of entities that have a text')
START_TIME = Summary('start_processing_seconds', 'Time spent in the /start handler')
INSPIRE_TIME = Summary('inspire_processing_seconds', 'Time spent in the /inspire handler')
INLINE_TIME = Summary('inline_processing_seconds', 'Time spent in the inline query handler')
CHOSEN_INLINE_RESULTS = Counter('chosen_inline_results', 'Amount of inline results that were chosen by a user')
