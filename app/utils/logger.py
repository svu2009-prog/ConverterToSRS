from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


class LogManager:
    _instance: Optional["LogManager"] = None
    _handler: Optional[logging.Handler] = None

    def __new__(cls) -> "LogManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def setup(self, log_dir: Optional[str] = None) -> None:
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "app.log")

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    def add_gui_handler(self, handler: logging.Handler) -> None:
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
