import sys
import json

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt

# UI Components
from ui.components.search_bar import SearchBar
from ui.components.table_widget import TableWidget
from ui.components.pagination import Pagination
from ui.components.spinner import Spinner

# Api Client
from ui.api.api_client import ApiClient
from ui.api.data_fetcher_thread import DataFetcherThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.api_client = ApiClient()
        self.get_pickings()

    def init_ui(self):
        
        self.setWindowTitle("CosPacks")
        self.setMinimumSize(1500, 600)
    
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("配 送 管 理")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        self.search_bar = SearchBar()
        self.search_bar.on_search.connect(lambda search_text: self.get_pickings())
        main_layout.addWidget(self.search_bar)

        self.table = TableWidget()
        self.table.selection_updated.connect(lambda row_count, selected_count: self.update_selection(row_count, selected_count))
        main_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        self.pagination = Pagination()
        self.pagination.on_page_changed.connect(self.on_page_changed)
        self.pagination.on_page_size_changed.connect(self.on_page_size_changed)
        bottom_layout.addWidget(self.pagination)

        self.selected_records = QLabel("0 / 0")
        bottom_layout.addWidget(self.selected_records)

        bottom_layout.addStretch()

        self.shipping_btn = QPushButton("運送会社")
        self.shipping_btn.clicked.connect(self.do_shipping)
        bottom_layout.addWidget(self.shipping_btn)

        self.exit_btn = QPushButton("退出")
        self.exit_btn.clicked.connect(QApplication.quit)
        bottom_layout.addWidget(self.exit_btn)

        main_layout.addLayout(bottom_layout)

        self.spinner = Spinner(self)
        self.shipping_btn.setFocus()

    def get_pickings(self):
        self.spinner.start()
        self.data_thread = DataFetcherThread(self.api_client, "get-pickings", {
            "query": self.search_bar.get_text(),
            "skip": self.pagination.get_page_size() * (self.pagination.get_current_page()),
            "limit": self.pagination.get_page_size()
        })
        self.data_thread.data_fetched.connect(lambda resp: self.update_table(resp))
        self.data_thread.error_occurred.connect(self.show_error)
        self.data_thread.start()

    def do_shipping(self):
        self.spinner.start()
        self.shipping_thread = DataFetcherThread(self.api_client, "do-shipping", {})
        self.shipping_thread.data_fetched.connect(lambda data: self.show_message("こんにちは。\n発送は無事完了しました。"))
        self.shipping_thread.error_occurred.connect(self.show_error)
        self.shipping_thread.start()

    def update_table(self, resp):
        if "pickings" in resp:
            self.table.update_table(resp["pickings"], resp["total"])
            self.pagination.update_item_count(resp["total"])
        self.spinner.stop()

    def update_selection(self, row_count, selected_count):
        self.selected_records.setText(f" {row_count} / {selected_count}")

    def show_message(self, message):
        self.spinner.stop()
        msg = QMessageBox(self)
        msg.setText(message)
        msg.setWindowTitle("運送会社")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def show_error(self, message):
        self.spinner.stop()
        QMessageBox.critical(self, "Error", message)

    # Signals

    def on_page_changed(self):
        self.get_pickings()
    
    def on_page_size_changed(self):
        self.get_pickings()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
