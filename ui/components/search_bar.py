import os
from PySide6.QtWidgets import ( QWidget, QHBoxLayout, QLineEdit, QPushButton )
from PySide6.QtCore import Qt, Signal

class SearchBar(QWidget):

    on_search = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setStyleSheet("padding: 7px;")
        self.search_edit.setPlaceholderText("検索語を入力してください...")
        
        self.search_button = QPushButton("検 索")
        self.search_button.setStyleSheet("QPushButton { padding: 6px; }")
        self.search_button.clicked.connect(self.on_search_button_clicked)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)
        search_layout.setAlignment(Qt.AlignLeft)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(search_layout)
    
    def on_search_button_clicked(self):
        self.on_search.emit(self.search_edit.text())
    def get_text(self):
        return self.search_edit.text()
