from PyQt5.QtWidgets import QWidget


class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.initUI()
        self.load_save_dir()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("苏丹的存档")
        self.show()

    def load_save_dir(self):
        # This method is called after the UI is initialized
        pass
