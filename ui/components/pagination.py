from PySide6.QtWidgets import ( QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox )
from PySide6.QtCore import Qt, Signal


class Pagination(QWidget):

    on_page_size_changed = Signal()
    on_page_changed = Signal()

    def __init__(self):
        super().__init__()

        self.item_count = 0
        self.current_page = 0
        self.page_size = 15

        self.init_ui()
        self.update_page()

    def init_ui(self):
        # Controls row
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Per-page ComboBox
        controls_layout.addWidget(QLabel("カウント:"))
        self.page_size_selector = QComboBox()
        self.page_size_selector.addItems(["15", "25", "50"])
        self.page_size_selector.setStyleSheet("QComboBox { width: 25px; height: 25px;}")
        self.page_size_selector.setCurrentText(str(self.page_size))
        self.page_size_selector.currentTextChanged.connect(self.change_page_size)
        controls_layout.addWidget(self.page_size_selector)

        # Previous button
        self.prev_btn = QPushButton("←")
        self.prev_btn.setStyleSheet("QPushButton { padding: 0px 0px; width: 25px; height: 28px;}")
        self.prev_btn.clicked.connect(self.prev_page)
        controls_layout.addWidget(self.prev_btn)

        # Page label
        self.page_label = QLabel()
        controls_layout.addWidget(self.page_label)

        # Next button
        self.next_btn = QPushButton("→")
        self.next_btn.setStyleSheet("QPushButton { padding: 0px; width: 25px; height: 28px;}")
        self.next_btn.clicked.connect(self.next_page)
        controls_layout.addWidget(self.next_btn)

        self.setLayout(controls_layout)

    def update_item_count(self, item_count):
        self.item_count = item_count
        self.update_page()

    def update_page(self):

        total_pages = max(1, (self.item_count + self.page_size - 1) // self.page_size)

        # Clamp current page
        self.current_page = max(0, min(self.current_page, total_pages - 1))

        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

    def prev_page(self):
        self.current_page -= 1
        self.on_page_changed.emit()

    def next_page(self):
        self.current_page += 1
        self.on_page_changed.emit()

    def change_page_size(self, value):
        self.page_size = int(value)
        self.current_page = 0
        self.on_page_size_changed.emit()

    def get_current_page(self):
        return self.current_page
    
    def get_page_size(self):
        return self.page_size
