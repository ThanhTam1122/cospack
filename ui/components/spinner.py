import os
from PySide6.QtWidgets import ( QWidget, QLabel, QGraphicsBlurEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie

class Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blur_radius = 3
        self.setParent(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # <== Important!
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 50);")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setGeometry(parent.rect())

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.parent().width(), self.parent().height())

        self.make_bg_blur(self.blur_radius)
        self.spinner_label = QLabel(self)
        self.spinner_label.setGeometry(parent.rect())
        gif_path = os.path.abspath("./ui/assets/spinner.gif")
        self.movie = QMovie(gif_path)

        self.movie.setSpeed(200)
        self.movie.setBackgroundColor(Qt.transparent)
        self.movie.setScaledSize(QSize(50, 50))

        self.spinner_label.setMovie(self.movie)
        self.spinner_label.setAlignment(Qt.AlignCenter)

        self.hide()

    def make_bg_blur(self, blur_radius):
        
        pixmap = self.parent().grab()
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)

        # Step 2: Apply blur to background only
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(blur_radius)
        self.background.setGraphicsEffect(self.blur_effect)

    def start(self):
        self.setGeometry(self.parent().rect())
        self.make_bg_blur(self.blur_radius)
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()
