import sys
import os
import requests
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

from ui.search_bar import SearchBar
from ui.table_widget import TableWidget
from ui.pagination import Pagination
from ui.spinner import Spinner

class ApiClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000/api")
        print(f"======== Connecting to backend at: {self.base_url} ==========")

    def get_pickings(self):
        try:
            print("======== API Get Pickings ==========")
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()
            time.sleep(2)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []

    def shipping(self):
        try:
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()
            time.sleep(3)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []

class DataFetcherThread(QThread):
    data_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_client):
        print("======== Init DataFetch Thread ========")
        super().__init__()
        self.api_client = api_client

    def run(self):
        try:
            resp = self.api_client.get_pickings()
            if "pickings" in resp:
                self.data_fetched.emit(resp["pickings"])
            else:
                self.data_fetched.emit([])
        except Exception as e:
            self.error_occurred.emit(str(e))

class ShippingThread(QThread):
    data_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    def run(self):
        try:
            resp = self.api_client.shipping()
            if "pickings" in resp:
                self.data_fetched.emit(resp["pickings"])
            else:
                self.data_fetched.emit([])
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.api_client = ApiClient()
        # self.load_data()

    def init_ui(self):
        
        self.setWindowTitle("配 送 管 理")
        self.setMinimumSize(1500, 600)
    
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("配 送 管 理")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        self.search_bar = SearchBar()
        self.search_bar.on_search.connect(lambda search_text: self.load_data())
        main_layout.addWidget(self.search_bar)

        self.table = TableWidget()
        self.table.selection_updated.connect(lambda row_count, selected_count: self.update_selection(row_count, selected_count))
        main_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        self.pagenation = Pagination()
        bottom_layout.addWidget(self.pagenation)

        self.total_records = QLabel("全件数: 0")
        self.selected_records = QLabel("選択件数: 0")
        bottom_layout.addWidget(self.total_records)
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

    def load_data(self):
        self.spinner.start()
        self.data_thread = DataFetcherThread(self.api_client)
        self.data_thread.data_fetched.connect(self.update_table)
        self.data_thread.error_occurred.connect(self.show_error)
        self.data_thread.start()

    def do_shipping(self):
        self.spinner.start()
        self.shipping_thread = ShippingThread(self.api_client)
        self.shipping_thread.data_fetched.connect(lambda data: self.show_message("運送会社のデータを取得しました"))
        self.shipping_thread.error_occurred.connect(self.show_error)
        self.shipping_thread.start()

    def update_table(self, items):
        self.table.setRowCount(0)
        self.table.update_table(items)
        self.spinner.stop()

    def update_selection(self, row_count, selected_count):
        self.selected_records.setText(f"選択件数: {selected_count}")
        self.total_records.setText(f"全件数: {row_count}")

    def show_message(self, message):
        self.spinner.stop()
        msg = QMessageBox(self)
        msg.setText(message)
        msg.setWindowTitle("運送会社")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: white;
                font-family: Arial;
                font-size: 14px;
                text-align: center;
            }
            QPushButton {
                background-color: #3c8dbc;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #559ed5;
            }
        """)
        msg.exec()

    def show_error(self, message):
        self.spinner.stop()
        QMessageBox.critical(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
