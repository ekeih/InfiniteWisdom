from prometheus_client import Gauge, Counter, Summary

POOL_SIZE = Gauge('pool_size', 'Size of the URL pool')
TELEGRAM_ENTITIES_COUNT = Gauge('telegram_entities_count',
                                'Number of items that have been uploaded to telegram servers')
IMAGE_ANALYSIS_TYPE_COUNT = Gauge('image_analysis_type_tesseract_count',
                                  'Number of entities that have been analysed by a specific analyser',
                                  ['type'])
IMAGE_ANALYSIS_HAS_TEXT_COUNT = Gauge('image_analysis_has_text_count',
                                      'Number of entities that have a text')
START_TIME = Summary('start_processing_seconds', 'Time spent in the /start handler')
INSPIRE_TIME = Summary('inspire_processing_seconds', 'Time spent in the /inspire handler')
INLINE_TIME = Summary('inline_processing_seconds', 'Time spent in the inline query handler')
CHOSEN_INLINE_RESULTS = Counter('chosen_inline_results', 'Amount of inline results that were chosen by a user')
