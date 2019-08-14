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
from prometheus_client.metrics import MetricWrapperBase

from infinitewisdom.const import IMAGE_ANALYSIS_TYPE_GOOGLE_VISION, IMAGE_ANALYSIS_TYPE_AZURE, \
    IMAGE_ANALYSIS_TYPE_TESSERACT

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

REGULAR_INTERVAL_WORKER_TIME = Summary('regular_interval_worker_processing_seconds',
                                       'Time spent for a single run cycle of this workercrawler run cycle',
                                       ['name'])

CRAWLER_TIME = REGULAR_INTERVAL_WORKER_TIME.labels(name="crawler")
UPLOADER_TIME = REGULAR_INTERVAL_WORKER_TIME.labels(name="uploader")
ANALYSER_TIME = REGULAR_INTERVAL_WORKER_TIME.labels(name="analyser")

ANALYSER_FIND_TEXT_TIME = Summary('analyser_find_text_processing_seconds',
                                  'Time spent to find text for a given image',
                                  ['name'])

GOOGLE_VISION_FIND_TEXT_TIME = ANALYSER_FIND_TEXT_TIME.labels(name=IMAGE_ANALYSIS_TYPE_GOOGLE_VISION)
MICROSOFT_AZURE_FIND_TEXT_TIME = ANALYSER_FIND_TEXT_TIME.labels(name=IMAGE_ANALYSIS_TYPE_AZURE)
TESSERACT_FIND_TEXT_TIME = ANALYSER_FIND_TEXT_TIME.labels(name=IMAGE_ANALYSIS_TYPE_TESSERACT)

ANALYSER_CAPACITY = Gauge('analyser_remaining_monthly_capacity',
                          'Current capacity of a given analyser',
                          ['name'])


def get_metrics() -> []:
    entries = set()
    for name, obj in globals().items():
        if isinstance(obj, MetricWrapperBase):
            entries.add(obj)

    return list(entries)


def format_metrics() -> str:
    def format_sample(sample):
        result = "  "
        if len(sample[0]) > 0:
            result += str(sample[0])
        if len(sample[1]) > 0:
            result += str(sample[1])

        if len(result) > 0:
            result += " "
        result += str(sample[2])

        return result

    def format_samples(samples):
        return "\n".join(list(map(format_sample, samples)))

    def format_metric(metric):
        name = metric._name
        samples = list(metric._samples())
        samples_text = format_samples(samples)

        return "{}:\n{}".format(name, samples_text)

    return "\n\n".join(map(format_metric, get_metrics()))
