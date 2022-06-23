import logging
import os
import sys
from logging import StreamHandler

DATE_FMT = "%Y-%m-%d %H:%M:%S"


class ColorFormatter(logging.Formatter):

    def __init__(self, fmt):
        super().__init__()

        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        self.formats = {
            logging.DEBUG: logging.Formatter(grey + fmt + reset, datefmt=DATE_FMT),
            logging.INFO: logging.Formatter(grey + fmt + reset, datefmt=DATE_FMT),
            logging.WARNING: logging.Formatter(yellow + fmt + reset, datefmt=DATE_FMT),
            logging.ERROR: logging.Formatter(red + fmt + reset, datefmt=DATE_FMT),
            logging.CRITICAL: logging.Formatter(bold_red + fmt + reset, datefmt=DATE_FMT)
        }

    def format(self, record):
        return self.formats[record.levelno].format(record)


stdout_logger = logging.getLogger("default")

if os.environ.get("LOGGING", "1"):
    stdout_logger.setLevel(logging.DEBUG)
else:
    stdout_logger.setLevel(logging.FATAL)

for h in stdout_logger.handlers:
    stdout_logger.removeHandler(h)

handler = StreamHandler(sys.stdout)
handler.formatter = ColorFormatter("%(asctime)s %(levelname)-5s>%(message)s")

stdout_logger.addHandler(handler)
logger = stdout_logger
