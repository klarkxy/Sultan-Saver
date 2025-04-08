import os
from util.config import Config

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from util.logger import logger

log = logger(__name__)


class WatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)


def start_observer(path: str):
    if not os.path.exists(path):
        log.fatal(f"Path does not exist: {path}")
        raise FileNotFoundError(f"Path does not exist: {path}")

    observer = Observer()
    observer.schedule(WatchHandler(), path, recursive=True)
    observer.start()
    log.debug(f"Watching for changes in {path}...")

    return observer
