import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFormLayout, QMessageBox, QHeaderView,
    QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests
import json


class ApiClient:
    """Client to interact with the FastAPI backend"""
    
    def __init__(self, base_url=None):
        # Get backend URL from environment variable or use default
        self.base_url = base_url or os.environ.get("BACKEND_URL", "http://localhost:8000/api")
        print(f"Connecting to backend at: {self.base_url}")
    
    def get_items(self):
        response = requests.get(f"{self.base_url}/items/")
        return response.json()
    
    def create_item(self, item_data):
        response = requests.post(
            f"{self.base_url}/items/",
            data=json.dumps(item_data),
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    def update_item(self, item_id, item_data):
        response = requests.put(
            f"{self.base_url}/items/{item_id}",
            data=json.dumps(item_data),
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    def delete_item(self, item_id):
        response = requests.delete(f"{self.base_url}/items/{item_id}")
        return response.status_code == 204


class DataFetcherThread(QThread):
    """Thread for fetching data from API"""
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        try:
            items = self.api_client.get_items()
            self.data_fetched.emit(items)
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
        self.api_client = ApiClient()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("Shipping Application")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Shipping Items Management")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Price", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        main_layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
    
    def load_data(self):
        self.data_thread = DataFetcherThread(self.api_client)
        self.data_thread.data_fetched.connect(self.update_table)
        self.data_thread.error_occurred.connect(self.show_error)
        self.data_thread.start()
    
    def update_table(self, items):
        self.table.setRowCount(0)
        
        for row, item in enumerate(items):
            self.table.insertRow(row)
            
            # Add item data
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("description", "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get("price", ""))))
            
            # Action buttons
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget = QWidget()
            
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, i=item: self.edit_item(i))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, i=item: self.delete_item(i))
            actions_layout.addWidget(delete_button)
            
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)
    
    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec_():
            try:
                new_item = self.api_client.create_item(dialog.get_item_data())
                self.load_data()
            except Exception as e:
                self.show_error(str(e))
    
    def edit_item(self, item):
        dialog = ItemDialog(self, item)
        if dialog.exec_():
            try:
                updated_item = self.api_client.update_item(
                    item["id"], dialog.get_item_data()
                )
                self.load_data()
            except Exception as e:
                self.show_error(str(e))
    
    def delete_item(self, item):
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete {item['name']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                success = self.api_client.delete_item(item["id"])
                if success:
                    self.load_data()
            except Exception as e:
                self.show_error(str(e))
    
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 