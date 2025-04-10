# -*- coding: utf-8 -*-
import yaml
import atexit
import os

from typing import List

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
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as file:
            Config._config = yaml.safe_load(file)


def save_data():
    with open("config.yaml", "w") as file:
        yaml.dump(Config._config, file)


atexit.register(save_data)
load_data()
