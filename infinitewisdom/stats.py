from prometheus_client import Gauge, Summary

POOL_SIZE = Gauge('pool_size', 'Size of the URL pool')
START_TIME = Summary('start_processing_seconds', 'Time spent in the /start handler')
INSPIRE_TIME = Summary('inspire_processing_seconds', 'Time spent in the /inspire handler')
INLINE_TIME = Summary('inline_processing_seconds', 'Time spent in the inline query handler')
