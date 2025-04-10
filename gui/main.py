# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QListWidget, QVBoxLayout, QFrame, QFileDialog
import os

from model.timeline import TimeLine
from util.config import Config


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
        
        self.time_line = TimeLine(self)

    def init_ui(self):
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
        # 分隔符
        self.file_menu.addSeparator()
        # 打开
        self.open_action = self.file_menu.addAction("打开")
        self.open_action.triggered.connect(self.open_save_dir)
        # 保存
        self.save_action = self.file_menu.addAction("保存")
        self.save_action.triggered.connect(self.save)
        # 另存为
        self.save_as_action = self.file_menu.addAction("另存为")
        self.save_as_action.triggered.connect(self.save_as)
        # 退出
        self.exit_action = self.file_menu.addAction("退出")
        self.exit_action.triggered.connect(self.exit)
        
        # 关于
        self.about_menu = self.menu_bar.addMenu("关于")
        self.about_action = self.about_menu.addAction("关于")
        self.about_action.triggered.connect(self.about)
    
    def on_time_line_loaded(self, round_files):
        # 存档时间线更新
        pass

    def change_save_dir(self):
        # 修改存档位置
        save_dir = QFileDialog.getExistingDirectory(None, "选择存档目录", Config.get("SaveDataDir"))
        if save_dir:
            Config.set("steam_id", os.path.basename(save_dir))
            Config.set("SaveDataDir", '\\'.join(save_dir.split('/')[:-1]))
            self.time_line = TimeLine(self)

