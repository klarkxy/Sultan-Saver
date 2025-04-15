# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QListWidget,
    QVBoxLayout,
    QFrame,
    QFileDialog,
)
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util.config import Config

_ignore_json = [
    "over_record_excerpt.json",
    "global.json",
    "global.json.bak.json",
]


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

        self.observer = None
        self.init_saves()

    def init_saves(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
        # 初始化存档
        self.save_dir = os.path.join(Config.get("SaveDataDir"), Config.get("steam_id"))
        self.round_raw_files = []
        # 根据最新的存档来导入之前所有的存档
        for file in os.listdir(self.save_dir):
            if file.endswith(".json") and file.startswith("round_"):
                self.round_raw_files.append(os.path.join(self.save_dir, file))
        # 按照修改时间排序倒序
        self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        # 然后开始监控
        self.observer = Observer()
        self.observer.schedule(self, self.save_dir, recursive=False)
        self.observer.start()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        if os.path.basename(event.src_path) not in _ignore_json:
            # 如果是回合存档文件
            self.round_raw_files.append(event.src_path)
            # 按照修改时间排序倒序
            self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    def on_modified(self, event):
        if os.path.basename(event.src_path) not in _ignore_json:
            # 按照修改时间排序倒序
            self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    def init_ui(self):
        # 窗口初始化
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(f"苏丹的存档（{Config.get('steam_id')}）")

        self.init_menu()
        self.init_content()

        self.show()

    def init_content(self):
        # 内容区域
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建左右布局
        layout = QHBoxLayout(central_widget)
        central_widget.setLayout(layout)

        # 左侧列表区域 (占1份宽度)
        self.list_widget = QListWidget(layout)
        layout.addWidget(self.list_widget, 1)

        # 右侧内容区域 (占3份宽度)
        self.content_frame = QFrame(layout)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.content_frame, 3)

        # 可以为右侧内容区域设置单独的布局
        content_layout = QVBoxLayout(self.content_frame)
        self.content_frame.setLayout(content_layout)

    def init_menu(self):
        # 菜单栏
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("文件")

        # 修改存档位置
        self.change_save_dir_action = self.file_menu.addAction("修改游戏存档位置")
        self.change_save_dir_action.triggered.connect(self.change_save_dir)

        # 关于
        self.about_menu = self.menu_bar.addMenu("关于")
        self.about_action = self.about_menu.addAction("关于")
        self.about_action.triggered.connect(self.about)

    def on_time_line_loaded(self, round_files):
        # 存档时间线更新
        pass

    def change_save_dir(self):
        # 修改存档位置
        save_dir = QFileDialog.getExistingDirectory(
            None, "选择存档目录", Config.get("SaveDataDir")
        )
        if save_dir:
            Config.set("steam_id", os.path.basename(save_dir))
            Config.set("SaveDataDir", "\\".join(save_dir.split("/")[:-1]))
            self.init_saves()
