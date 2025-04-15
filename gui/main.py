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
    QTextEdit,
)
import os

import json
import ijson

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
        for file in os.listdir(self.save_dir):
            if file.endswith(".json"):
                self.round_raw_files.append(os.path.join(self.save_dir, file))
        # 按照修改时间排序倒序
        self.round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        # 然后开始监控
        self.observer = Observer()
        self.observer.schedule(self, self.save_dir, recursive=False)
        self.observer.start()
        # 刷新存档列表
        self.refresh_save_list()

    def handle_header_clicked(self, column):
        # 如果点击的是当前排序列，则反转排序方向
        if column == self.sort_column:
            self.sort_order = not self.sort_order
        else:
            # 否则设置为新列，默认升序
            self.sort_column = column
            self.sort_order = False

        # 根据列类型进行排序
        if self.sort_column == 0:  # 存档名称(字符串)
            self.round_raw_files.sort(
                key=lambda x: os.path.basename(x).lower(), reverse=self.sort_order
            )
        else:  # 修改时间(日期)
            self.round_raw_files.sort(
                key=lambda x: os.path.getmtime(x), reverse=self.sort_order
            )

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
            # 如果是回合存档文件，在列表最前面增加
            self.round_raw_files.insert(0, event.src_path)
            # 刷新存档列表
            self.refresh_save_list()

    def on_modified(self, event):
        if os.path.basename(
            event.src_path
        ) not in _ignore_json and event.src_path.endswith(".json"):
            # 按照修改时间排序倒序，找到列表中对应文件的位置并置顶
            self.round_raw_files.remove(event.src_path)
            self.round_raw_files.insert(0, event.src_path)
            # 刷新存档列表
            self.refresh_save_list()

    def init_ui(self):
        # 窗口初始化
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(f"苏丹的存档（{Config.get('steam_id')}）")

        # 排序状态
        self.sort_column = 0
        self.sort_order = False  # False=升序, True=降序

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
        self.table_widget.setColumnWidth(0, 200)  # 存档名称
        self.table_widget.setColumnWidth(1, 100)  # 修改时间
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().sectionClicked.connect(
            self.handle_header_clicked
        )
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为只读模式
        self.table_widget.itemSelectionChanged.connect(self.update_save_info)
        layout.addWidget(self.table_widget, 1)

        # 右侧内容区域
        self.content_frame = QFrame(central_widget)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        layout.addWidget(self.content_frame, 1)

        # 右侧内容区域布局
        content_layout = QVBoxLayout(self.content_frame)
        self.content_frame.setLayout(content_layout)

        # 添加重命名输入框和按钮
        rename_layout = QHBoxLayout()
        self.rename_input = QTextEdit(self.content_frame)
        self.rename_input.setMaximumHeight(30)
        self.rename_input.setPlaceholderText("输入新存档名")
        rename_layout.addWidget(self.rename_input, 1)

        self.rename_btn_top = QPushButton("另存为", self.content_frame)
        self.rename_btn_top.clicked.connect(self.rename_save_from_input)
        rename_layout.addWidget(self.rename_btn_top)
        content_layout.addLayout(rename_layout)

        # 存档信息显示区域
        self.save_info_text = QTextEdit(self.content_frame)
        self.save_info_text.setReadOnly(True)
        content_layout.addWidget(self.save_info_text)

        # 添加操作按钮
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("加载存档", self.content_frame)
        self.load_btn.clicked.connect(self.load_save)
        btn_layout.addWidget(self.load_btn)
        content_layout.addLayout(btn_layout)

        # 添加拉伸使按钮在上方
        content_layout.addStretch()

    def init_menu(self):
        # 菜单栏
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("文件")

        # 修改存档位置
        self.change_save_dir_action = self.file_menu.addAction("修改游戏存档位置")
        self.change_save_dir_action.triggered.connect(self.change_save_dir)

        # 打开存档目录
        self.open_save_dir_action = self.file_menu.addAction("打开存档目录")
        self.open_save_dir_action.triggered.connect(self.open_save_dir)

        # 关于
        self.about_menu = self.menu_bar.addMenu("关于")
        self.about_action = self.about_menu.addAction("关于")
        self.about_action.triggered.connect(self.about)

    def about(self):
        # 关于对话框
        QMessageBox.about(self, "关于", util.version.about_text())

    def open_save_dir(self):
        # 打开存档目录
        if hasattr(self, "save_dir") and os.path.exists(self.save_dir):
            os.startfile(self.save_dir)
        else:
            QMessageBox.warning(self, "警告", "存档目录不存在或未初始化")

    def get_choiced_save_path(self) -> str:
        selected = self.table_widget.currentItem()
        if not selected:
            self.save_info_text.clear()
            self.rename_input.clear()
            return None

        # 获取选中的存档路径
        row = selected.row()
        save_path = self.table_widget.item(row, 0).data(1)
        if not save_path:
            self.save_info_text.clear()
            self.rename_input.clear()
            return None
        return save_path

    def update_save_info(self):
        # 更新存档信息
        save_path = self.get_choiced_save_path()
        if save_path is None:
            return
        file_name = os.path.basename(save_path)
        if file_name.endswith(".json"):
            save_name = file_name[:-5]  # 去掉.json后缀
            self.rename_input.setPlainText(save_name)

        try:
            with open(save_path, "r", encoding="utf8") as f:
                save_data = json.load(f)

            character_name = save_data.get("name", "未知")
            difficulty = save_data.get("difficulty", "未知")
            current_round = save_data.get("round", "未知")
            save_time_str = save_data.get("saveTime", "")
            try:
                if save_time_str:
                    save_time_dt = datetime.fromisoformat(
                        save_time_str.replace("Z", "+00:00")
                    )
                    save_time = save_time_dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    save_time = "未知"
            except ValueError:
                save_time = "未知"

            info_text = f"""存档详细信息:
主角名: {character_name}
游戏难度: {difficulty}
当前回合: {current_round}
保存时间: {save_time}
"""
            self.save_info_text.setPlainText(info_text)
        except Exception as e:
            self.save_info_text.setPlainText(f"读取存档信息失败: {str(e)}")

    def rename_save_from_input(self):
        selected = self.table_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要另存为的存档")
            return

        new_name = self.rename_input.toPlainText().strip()
        if not new_name:
            QMessageBox.warning(self, "警告", "请输入新存档名")
            return

        old_path = self.get_choiced_save_path()
        new_path = os.path.join(os.path.dirname(old_path), f"{new_name}.json")

        # 检查文件是否已存在
        if os.path.exists(new_path):
            reply = QMessageBox.question(
                self,
                "确认",
                "同名存档已存在，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        try:
            # 复制而不是重命名文件
            with open(old_path, "r", encoding="utf-8") as src:
                data = src.read()
            with open(new_path, "w", encoding="utf-8") as dst:
                dst.write(data)

            self.init_saves()  # 刷新列表
            QMessageBox.information(self, "成功", "存档另存为成功")
            self.rename_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"另存为失败: {str(e)}")

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
