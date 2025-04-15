import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,QAbstractButton,
    QLabel, QLineEdit, QMessageBox, QHeaderView,QAbstractItemView,
    QSpacerItem, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QMovie
import requests
import time

class ApiClient:
    """Client to interact with the FastAPI backend"""
    
    def __init__(self, base_url=None):
        # Get backend URL from environment variable or use default
        self.base_url = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000/api")
        print(f"======== Connecting to backend at: {self.base_url} ==========")
    
    def get_pickings(self):
        try:
            print("======== API Get Pickings ==========")
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            time.sleep(1)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []  # Return an empty list or handle the error as needed
    def shipping(self):
        try:
            response = requests.get(f"{self.base_url}/pickings/")
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            print("======== API Get Shipping ==========")
            time.sleep(2)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []
class DataFetcherThread(QThread):
    """Thread for fetching data from API"""
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
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
    """Thread for fetching data from API"""
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client):
        print("======== Init Shipping Thread ========")
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

class SpinnerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setParent(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # <== Important!
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 25);")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setGeometry(parent.rect())

        self.spinner_label = QLabel(self)
        self.spinner_label.setGeometry(parent.rect())
        gif_path = os.path.abspath("./ui/spinner.gif")
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
class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.api_client = ApiClient()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("配 送 管 理")
        self.setMinimumSize(1500, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("配 送 管 理")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("検索語を入力してください...")
        self.search_edit.setStyleSheet("font-size: 16px; padding: 7px; border-radius: 5px; border: 1px solid #ccc;")
        self.search_button = QPushButton("検 索")
        self.search_button.setStyleSheet("QPushButton { background-color: #115181;color: white;border-radius: 5px;padding: 8px; font-size: 16px;font-weight: bold;border: none; min-width: 100px;}QPushButton:hover {    background-color: #1c5c8e;}QPushButton:pressed {    background-color: #2c699a;}")
        self.search_button.clicked.connect(self.load_data)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)
        search_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setHorizontalHeaderLabels(["","Id", "出荷日付", "ピッキング連番", "ピッキング日", "ピッキング時刻", "受注No_From", "受注No_To", "得意先CD_From", "得意先CD_To", "得意先略称", "担当者CD", "担当者略称"])
        self.table.horizontalHeader().setSectionResizeMode(12, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 20)  # First column (checkbox)
        self.table.setColumnHidden(1, True)
        self.table.setStyleSheet("QHeaderView::section { padding: 8px; padding-left: 10px; font-size: 14px;}")
        self.table.clicked.connect(self.on_row_click)

        checkbox_all = QCheckBox()
        checkbox_all.setChecked(False)
        checkbox_all.stateChanged.connect(self.toggle_select_all)
        widget = QWidget(self.table.horizontalHeader())
        layout = QHBoxLayout(widget)
        widget.setStyleSheet("QWidget { padding-top: 6px; }")
        layout.setAlignment(Qt.AlignCenter)  # Center the checkbox
        layout.addWidget(checkbox_all)
        widget.setLayout(layout)
        self.table.setCellWidget(0, 0, widget)
        
        main_layout.addWidget(self.table)
        
        # Bottom Bar
        bottom_layout = QHBoxLayout()
        
        self.total_records = QLabel("全件数: 0")
        self.total_records.setStyleSheet("font-size: 16px; padding: 7px;")
        self.selected_records = QLabel("選択件数: 0")
        self.selected_records.setStyleSheet("font-size: 16px; padding: 7px;")
        bottom_layout.addWidget(self.total_records)
        bottom_layout.addWidget(self.selected_records)
        bottom_layout.addStretch()

        h_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottom_layout.addSpacerItem(h_spacer)

        self.shipping_btn = QPushButton("運送会社")
        self.shipping_btn.setStyleSheet("QPushButton { background-color: #3498db;color: white;border-radius: 5px;padding: 8px;font-size: 16px;font-weight: bold;border: none; min-width: 120px;}QPushButton:hover {    background-color: #2980b9;}QPushButton:pressed {    background-color: #1c598a;}")
        self.shipping_btn.clicked.connect(self.shipping)
        bottom_layout.addWidget(self.shipping_btn)
        
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setStyleSheet("QPushButton { background-color: #e74c3c;;color: white;border-radius: 5px;padding: 8px;font-size: 16px;font-weight: bold;border: none; min-width: 120px;}QPushButton:hover {    background-color: #c0392b;}QPushButton:pressed {    background-color: #a93226;}")
        self.exit_btn.clicked.connect(QApplication.quit)
        bottom_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(bottom_layout)

        self.spinner = SpinnerOverlay(self)
    
    def load_data(self):
        self.spinner.start()
        self.data_thread = DataFetcherThread(self.api_client)
        self.data_thread.data_fetched.connect(self.update_table)
        self.data_thread.error_occurred.connect(self.show_error)
        self.data_thread.start()
    
    def update_table(self, items):
        self.table.setRowCount(0)
        self.total_records.setText(f"全件数: {len(items)}")
        for row, item in enumerate(items):
            self.table.insertRow(row)
            
            # Add item data
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox.clicked.connect(lambda i=item: self.on_checkbox_clicked(i))
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table.setCellWidget(row, 0, checkbox_widget)

            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("picking_id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("picking_date", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("picking_time", "")))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("shipping_date", "")))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.get("order_no_from", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(str(item.get("order_no_to", ""))))
            self.table.setItem(row, 7, QTableWidgetItem(str(item.get("customer_code_from", ""))))
            self.table.setItem(row, 8, QTableWidgetItem(str(item.get("customer_code_to", ""))))
            self.table.setItem(row, 9, QTableWidgetItem(str(item.get("customer_short_name", ""))))
            self.table.setItem(row, 10, QTableWidgetItem(str(item.get("staff_code", ""))))
            self.table.setItem(row, 11, QTableWidgetItem(str(item.get("staff_short_name", ""))))
            self.table.setItem(row, 12, QTableWidgetItem(""))
        self.spinner.stop()

    def shipping (self):
        print("======== Shipping Button Clicked ========")
        self.spinner.start()
        self.data_thread = ShippingThread(self.api_client)
        self.data_thread.data_fetched.connect(lambda data: self.show_message(f"運送会社データが正常に取得されました。件数: {len(data)}"))
        self.data_thread.error_occurred.connect(self.show_error)
        self.data_thread.start()

    def on_checkbox_clicked(self, item):
        self.update_selected_row_count()

    def on_row_click(self, index):
        row = index.row()
        checkbox = self.table.cellWidget(row, 0).findChild(QCheckBox)
        if checkbox and checkbox.isChecked():
            checkbox.setChecked(False)
        else:
            checkbox.setChecked(True)
        self.update_selected_row_count()

    def toggle_select_all(self, state):
        if state == Qt.Checked:
            self.selected_records.setText(f"選択件数: {self.table.rowCount()}")
        else:
            self.selected_records.setText("選択件数: 0")

        for row in range(self.table.rowCount()):
            item = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if item:
                item.setCheckState(state)
            if state == Qt.Checked:
                for i in range(self.table.columnCount()):
                    item = self.table.item(row, i)
                    if item:
                        item.setSelected(True)
            else:
                for i in range(self.table.columnCount()):
                    item = self.table.item(row, i)
                    if item:
                        item.setSelected(False)

    def update_selected_row_count (self):
        selected_count = 0
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                selected_count += 1
                for i in range(self.table.columnCount()):
                    item = self.table.item(row, i)
                    if item:
                        item.setSelected(True)
            else:
                for i in range(self.table.columnCount()):
                    item = self.table.item(row, i)
                    if item:
                        item.setSelected(False)
        self.selected_records.setText(f"選択件数: {selected_count}")

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
        msg.exec_()
        self.spinner.stop()

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