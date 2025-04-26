# -*- coding: utf-8 -*-
import logging
import sys
import os

DEBUG = "--debug" in sys.argv


def logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    os.makedirs("log", exist_ok=True)

    # Set up file handler
    file_handler = logging.FileHandler(f"log/{name}.log")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    logger.propagate = False  # Prevent double logging to console
    logger.info(f"正在初始化 {name} 日志")
    return logger
