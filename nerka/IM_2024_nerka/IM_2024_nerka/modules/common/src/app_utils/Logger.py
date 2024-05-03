import logging
from datetime import datetime
from time import time


def get_logger() -> logging.Logger:
    return Logger.get_logger()


class Logger:
    logger = None

    FORMAT_STR = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

    @staticmethod
    def get_logger() -> logging.Logger:
        if Logger.logger is None:
            logging.basicConfig(format=Logger.FORMAT_STR)
            Logger.logger = logging.getLogger()
            try:
                Logger.logger.setLevel(level=logging.DEBUG)
                Logger.logger.addHandler(_FileFormattedHandler(logging.DEBUG))
                Logger.logger.addHandler(_FileFormattedHandler(logging.CRITICAL))
            except Exception as ex:
                Logger.logger.error(f'Exception occurred while getting logger: {ex, ex.with_traceback(ex.__traceback__)}')
        return Logger.logger


class _FileFormattedHandler(logging.FileHandler):
    LOG_PATH = './logs/'

    def __init__(self, level: int):
        super().__init__(_FileFormattedHandler.LOG_PATH + logging.getLevelName(level) + datetime.now().strftime('%Y_%m_%d') + '.log')
        super().setFormatter(logging.Formatter(Logger.FORMAT_STR))
        super().setLevel(level)


def log_execution(func):
    def execution_tracer(*args, **kwargs):
        get_logger().debug(f'Function {func.__qualname__} started.')
        start_time = time()
        ret = func(*args, **kwargs)
        get_logger().debug(f'Function {func.__qualname__} ended. Execution time: {(time() - start_time):.3f} s')
        return ret

    return execution_tracer
