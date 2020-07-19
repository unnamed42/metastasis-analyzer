from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from widgets import MainWindow

if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    exit(app.exec_())
