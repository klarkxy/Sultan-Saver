import yaml
import atexit
import os

from typing import List

class Config:
    _config = {}

    @staticmethod
    def get(key):
        return Config._config.get(key)

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

def find_save_data() -> str | List[str] | None:
    """
    寻找存档数据位置
    通常是在类似于“C:\Users\27837\AppData\LocalLow\DoubleCross\SultansGame\SAVEDATA\76561198095514219”的目录下
    """
    save_data_dir = os.path.join(
        os.getenv("LOCALAPPDATA")+"Low",
        "DoubleCross",
        "SultansGame",
        "SAVEDATA",
    )
    save_data_path = os.path.join(save_data_dir, Config.get("steam_id"),
    )
    if os.path.exists(save_data_path):
        return save_data_path
    elif os.path.exists(save_data_dir):
        save_data_path = []
        for file in os.listdir(save_data_dir):
            if os.path.isdir(os.path.join(save_data_dir, file)):
                save_data_path.append(os.path.join(save_data_dir, file))
        if len(save_data_path) == 1:
            return save_data_path[0]
        return save_data_path
    else:
        return None







def load_data():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as file:
            Config._config = yaml.safe_load(file)


def save_data():
    with open("config.yaml", "w") as file:
        yaml.dump(Config._config, file)


atexit.register(save_data)
load_data()
