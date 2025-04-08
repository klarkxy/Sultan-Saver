from PyQt5.QtWidgets import QApplication
import sys

from gui.main import MainWindow


def mainloop():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())
