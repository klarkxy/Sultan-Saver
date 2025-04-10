# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
import sys
import os

from gui.main import MainWindow
from util.config import Config

def find_save_data() -> str | list[str]:
    r"""
    寻找存档数据位置
    """
    save_data_dir = Config.getset("SaveDataDir",os.path.join(
        os.getenv("LOCALAPPDATA")+"Low",
        "DoubleCross",
        "SultansGame",
        "SAVEDATA",
    ))
    steam_id = Config.getset("steam_id")
    if not os.path.exists(save_data_dir):
        # 如果目录不存在，则返回空列表
        return []
    if steam_id is None:
        # 没有steam_id，先看一下目录里是否有唯一文件夹
        dirs = os.listdir(save_data_dir)
        if len(dirs) == 1:
            # 如果只有一个文件夹，则返回这个文件夹
            Config.set("steam_id", dirs[0])
            return os.path.join(save_data_dir, dirs[0])
        else:
            # 如果有多个文件夹，则返回空列表
            return []
    # 如果有steam_id，则返回这个文件夹
    save_data_path = os.path.join(save_data_dir, Config.get("steam_id"))
    if os.path.exists(save_data_path):
        return save_data_path
    else:
        return []

def mainloop():
    app = QApplication(sys.argv)
    
    # 先找到存档目录
    save_dir = find_save_data()
    if save_dir is None or isinstance(save_dir, list):
        # 如果有多个存档目录，则弹出文件夹选择框
        from PyQt5.QtWidgets import QFileDialog
        save_dir = QFileDialog.getExistingDirectory(None, "选择存档目录", Config.get("SaveDataDir"))
        if not save_dir:
            # 如果用户取消了选择，则退出程序
            sys.exit(0)
        # 取出最后的steam_id
        steam_id = os.path.basename(save_dir)
        Config.set("steam_id", steam_id)
    # 再创建窗口    
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())
