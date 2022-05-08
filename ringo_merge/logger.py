import logging


class ColoredFormatter(logging.Formatter):
    color_map = {
        logging.CRITICAL: '\033[91m',  # red
        logging.ERROR: '\033[91m',  # red
        logging.WARNING: '\033[93m',  # yellow
        logging.INFO: '\033[92m',  # green
        logging.DEBUG: '\033[94m',  # blue
    }
    reset_seq = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return self.color_map.get(record.levelno, '') + msg + self.reset_seq


def get_logger(level=logging.ERROR):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = ColoredFormatter()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


logger = get_logger(logging.DEBUG)
logging.captureWarnings(True)
logger.debug('init logger')
