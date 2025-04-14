import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,QAbstractButton,
    QLabel, QLineEdit, QFormLayout, QMessageBox, QHeaderView,QAbstractItemView,
    QDialog, QDialogButtonBox, QSpacerItem, QSizePolicy, QStyledItemDelegate, QStyle, QStyleOptionButton, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QRect, QEvent
from PyQt5.QtGui import QPainter
import requests
import json

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
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return []  # Return an empty list or handle the error as needed
        
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

class ItemDialog(QDialog):

    """Dialog for creating/editing items"""
    
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Item" if not self.item else "Edit Item")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        # Create form fields
        self.name_edit = QLineEdit(self)
        self.description_edit = QLineEdit(self)
        self.price_edit = QLineEdit(self)
        
        # Fill fields if editing
        if self.item:
            self.name_edit.setText(self.item.get("name", ""))
            self.description_edit.setText(self.item.get("description", ""))
            self.price_edit.setText(str(self.item.get("price", "")))
        
        # Add fields to layout
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Description:", self.description_edit)
        layout.addRow("Price:", self.price_edit)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_item_data(self):
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.text(),
            "price": float(self.price_edit.text() or 0)
        }

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
        bottom_layout.addWidget(self.shipping_btn)
        
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setStyleSheet("QPushButton { background-color: #e74c3c;;color: white;border-radius: 5px;padding: 8px;font-size: 16px;font-weight: bold;border: none; min-width: 120px;}QPushButton:hover {    background-color: #c0392b;}QPushButton:pressed {    background-color: #a93226;}")
        self.exit_btn.clicked.connect(QApplication.quit)
        bottom_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def load_data(self):
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

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 