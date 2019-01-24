import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def timeit(fn, msg=None):
    start = time.time()
    result = fn()
    duration = time.time() - start
    if msg:
        logger.debug(msg)
    logger.debug("Elapsed: %0.2f", duration)

    return result
