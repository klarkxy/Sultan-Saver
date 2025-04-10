import os
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util.config import Config

class TimeLine(FileSystemEventHandler):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.save_dir = os.path.join(Config.get("SaveDataDir"), Config.get("steam_id"))

        round_raw_files = []
        # 根据最新的存档来导入之前所有的存档
        for file in os.listdir(self.save_dir):
            if file.endswith(".json") and file.startswith("round_"):
                round_raw_files.append(os.path.join(self.save_dir, file))
        # 按照修改时间排序倒序
        round_raw_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        # 获取最新存档的回合数
        latest_file = round_raw_files[0]
        latest_file_name = os.path.basename(latest_file).split(".")[0]
        end = latest_file_name.endswith("_end")
        latest_round = int(latest_file_name.split("_")[1])
            
        # 载入所有的存档
        self.round_files = []
        for i in range(latest_round + 1):
            round_file = os.path.join(self.save_dir, f"round_{i}.json")
            round_end_file = os.path.join(self.save_dir, f"round_{i}_end.json")
            if os.path.exists(round_file):
                self.round_files.append(round_file)
            if os.path.exists(round_end_file):
                if i == latest_round and not end:
                    # 如果是最新的存档，并且不是回合末存档，说明不是当前存档
                    continue
                self.round_files.append(round_end_file)
        self.main_window.on_time_line_updated(self.round_files)

        # 然后开始监控
        self.observer = Observer()
        self.observer.schedule(self, self.save_dir, recursive=False)
        self.observer.start()
    
    def __del__(self):
        self.observer.stop()
        self.observer.join()

    def on_round_json_created_or_modified(self, event):
        file_name = os.path.basename(event.src_path).split(".")[0]
        round = int(file_name.split("_")[1])
        end = file_name.endswith("_end")
        
        # 找到新回合之前接入的位置
        while len(self.round_files) > 0:
            latest_file = self.round_files[-1]
            latest_file_name = os.path.basename(latest_file).split(".")[0]
            latest_round = int(latest_file_name.split("_")[1])
            latest_end = latest_file_name.endswith("_end")
            if latest_round == round and not latest_end or latest_round == round - 1 and latest_end:
                break
            self.round_files.pop()
        self.round_files.append(os.path.basename(event.src_path))
        self.main_window.on_time_line_updated(self.round_files)
    
    def on_created(self, event):
        if event.src_path.endswith(".json") and event.src_path.startswith("round_"):
            # 如果是回合存档文件
            self.on_round_json_created_or_modified(event)

    def on_modified(self, event):
        if event.src_path.endswith(".json") and event.src_path.startswith("round_"):
            # 如果是回合存档文件
            self.on_round_json_created_or_modified(event)