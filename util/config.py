# -*- coding: utf-8 -*-
import json
import atexit
import os


class Config:
    _config = {}

    @staticmethod
    def get(key, default=None):
        return Config._config.get(key, default)

    @staticmethod
    def set(key, value):
        Config._config[key] = value

    @staticmethod
    def getset(key, default=None):
        if key not in Config._config:
            Config._config[key] = default
        return Config._config[key]

    @staticmethod
    def __getitem__(key):
        return Config.get(key)

    @staticmethod
    def __setitem__(key, value):
        Config.set(key, value)

    @staticmethod
    def __contains__(key):
        return key in Config._config


def load_data():
    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            Config._config = json.load(file)


def save_data():
    with open("config.json", "w") as file:
        json.dump(Config._config, file)


atexit.register(save_data)
load_data()
