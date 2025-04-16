import os
from PySide6.QtWidgets import ( QWidget, QLabel )
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie

class Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setParent(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # <== Important!
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 25);")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setGeometry(parent.rect())

        self.spinner_label = QLabel(self)
        self.spinner_label.setGeometry(parent.rect())
        gif_path = os.path.abspath("./ui/assets/spinner.gif")
        self.movie = QMovie(gif_path)

        self.movie.setSpeed(100)
        self.movie.setScaledSize(QSize(50, 50))

        self.spinner_label.setMovie(self.movie)
        self.spinner_label.setAlignment(Qt.AlignCenter)

        self.hide()

    def start(self):
        self.setGeometry(self.parent().rect())
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()
