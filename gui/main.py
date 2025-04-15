# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QFrame,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QInputDialog,
)
import os

import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util.config import Config
from datetime import datetime
import util.version

_ignore_json = [
    "over_record_excerpt.json",
    "global.json",
    "global.json.bak.json",
    "auto_save.json",
]


class MainWindow(QMainWindow, FileSystemEventHandler):
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
        # 刷新存档列表
        self.refresh_save_list()

    def refresh_save_list(self):
        # 刷新存档列表
        self.table_widget.setRowCount(0)
        for file_path in self.round_raw_files:
            if (
                file_path.endswith(".json")
                and os.path.basename(file_path) not in _ignore_json
            ):
                file_name = os.path.basename(file_path)
                display_name = os.path.splitext(file_name)[0]
                mod_time = os.path.getmtime(file_path)
                time_str = datetime.fromtimestamp(mod_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)

                # 添加存档名称
                name_item = QTableWidgetItem(display_name)
                name_item.setData(1, file_path)  # 保持文件路径存储方式不变
                self.table_widget.setItem(row, 0, name_item)

                # 添加修改时间
                time_item = QTableWidgetItem(time_str)
                self.table_widget.setItem(row, 1, time_item)

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        if os.path.basename(
            event.src_path
        ) not in _ignore_json and event.src_path.endswith(".json"):
            # 如果是回合存档文件
            self.round_raw_files.append(event.src_path)
            # 按照修改时间排序倒序
            self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # 刷新存档列表
            self.refresh_save_list()

    def on_modified(self, event):
        if os.path.basename(
            event.src_path
        ) not in _ignore_json and event.src_path.endswith(".json"):
            # 按照修改时间排序倒序
            self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # 刷新存档列表
            self.refresh_save_list()

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

        # 左侧表格区域
        self.table_widget = QTableWidget(central_widget)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["存档名称", "修改时间"])
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为只读模式
        layout.addWidget(self.table_widget, 2)

        # 右侧内容区域
        self.content_frame = QFrame(central_widget)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.content_frame, 3)

        # 右侧内容区域布局
        content_layout = QVBoxLayout(self.content_frame)
        self.content_frame.setLayout(content_layout)

        # 添加操作按钮
        self.load_btn = QPushButton("加载存档", self.content_frame)
        self.load_btn.clicked.connect(self.load_save)
        content_layout.addWidget(self.load_btn)

        # 添加拉伸使按钮在上方
        content_layout.addStretch()

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

    def about(self):
        # 关于对话框
        QMessageBox.about(self, "关于", util.version.about_text())

    def rename_save(self):
        selected = self.table_widget.currentItem()
        if not selected:
            return

        old_path = selected.data(1)  # 路径仍然存储在data(1)中
        new_name, ok = QInputDialog.getText(
            self,
            "重命名存档",
            "输入新存档名(不带扩展名):",
            text=os.path.basename(old_path)[:-5],
        )
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), f"round_{new_name}.json")
            try:
                os.rename(old_path, new_path)
                self.init_saves()  # 刷新列表
            except Exception as e:
                QMessageBox.warning(self, "错误", f"重命名失败: {str(e)}")

    def load_save(self):
        selected = self.table_widget.currentItem()
        if not selected:
            return

        save_path = selected.data(1)
        save_dir = os.path.dirname(save_path)

        try:
            # 复制到auto_save.json
            with open(save_path, "r", encoding="utf-8") as src:
                data = src.read()
            with open(
                os.path.join(save_dir, "auto_save.json"), "w", encoding="utf-8"
            ) as dst:
                dst.write(data)

            # 修改global.json
            global_path = os.path.join(save_dir, "global.json")
            if os.path.exists(global_path):
                with open(global_path, "r+", encoding="utf-8") as f:
                    global_data = json.load(f)
                    global_data["inGame"] = True
                    f.seek(0)
                    json.dump(global_data, f, ensure_ascii=False, indent=2)
                    f.truncate()

            QMessageBox.information(self, "成功", "存档已加载")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载存档失败: {str(e)}")

    def change_save_dir(self):
        # 修改存档位置
        save_dir = QFileDialog.getExistingDirectory(
            None, "选择存档目录", Config.get("SaveDataDir")
        )
        if save_dir:
            Config.set("steam_id", os.path.basename(save_dir))
            Config.set("SaveDataDir", "\\".join(save_dir.split("/")[:-1]))
            self.init_saves()
