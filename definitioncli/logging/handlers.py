import logging
import sys
from pathlib import Path

from .formats import ColoredFormatter


class FileHandler(logging.FileHandler):
    def __init__(self, filename, mode="a", encoding=None, delay=False):
        # Ensure the directory exists
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the file handler
        super().__init__(filename, mode=mode, encoding=encoding, delay=delay)

        # Set a standard formatter without colors for the file handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.setFormatter(formatter)


class ConsoleHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream or sys.stdout)

        # Set the formatter that adds color codes
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.setFormatter(formatter)
