# -*- coding: utf-8 -*-
import logging


def logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    return logger
