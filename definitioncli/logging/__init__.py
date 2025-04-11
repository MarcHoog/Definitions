import logging
from .handlers import FileHandler, ConsoleHandler


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    file_handler = FileHandler("logs/app.log")
    logger.addHandler(file_handler)
    console_handler = ConsoleHandler()
    logger.addHandler(console_handler)
    return logger
