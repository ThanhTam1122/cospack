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

class PureCheckBox(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(20, 20)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)
        self._hovered = False

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.state |= QStyle.State_Enabled
        opt.state |= QStyle.State_On if self.isChecked() else QStyle.State_Off
        if self._hovered:
            opt.state |= QStyle.State_MouseOver

        opt.rect = self.rect()
        self.style().drawControl(QStyle.CE_CheckBox, opt, painter, self)

    def sizeHint(self):
        return QSize(20, 20)

class CheckBoxHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.is_checked = False

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)

        if logicalIndex == 0:  # First column header
            option = QStyleOptionButton()
            option.rect = self.checkboxRect(rect)
            option.state = QStyle.State_Enabled
            if self.is_checked:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off

            painter.save()
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)
            painter.restore()

    def checkboxRect(self, rect):
        """Calculate the position for the checkbox to be centered in the header cell."""
        checkbox_style = QStyleOptionButton()
        size = self.style().sizeFromContents(
            QStyle.CT_CheckBox, checkbox_style, QSize(20, 20), self
        )
        x = rect.x() + (rect.width() - size.width()) // 2
        y = rect.y() + (rect.height() - size.height()) // 2
        return QRect(x, y, size.width(), size.height())

    def mousePressEvent(self, event):
        """Handle click event in the header section."""
        index = self.logicalIndexAt(event.pos())
        if index == 0:  # If clicking on the first column's header
            section_rect = self.sectionRect(index)  # Get the rect for the header section
            if self.checkboxRect(section_rect).contains(event.pos()):
                self.is_checked = not self.is_checked
                self.updateSection(0)
                self.parent().selectAllRows(self.is_checked)
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        # uic.loadUi("layout.ui", self)
        self.init_ui()

        self.api_client = ApiClient()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("Shipping Application")
        self.setMinimumSize(1500, 600)
        
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
        self.table.setColumnCount(12)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["", "出荷日付", "ピッキング連番", "ピッキング日", "ピッキング時刻", "受注No_From", "受注No_To", "得意先CD_From", "得意先CD_To", "得意先略称", "担当者CD", "担当者略称"])
        self.table.horizontalHeader().setSectionResizeMode(11, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 20)  # First column (checkbox)
        self.table.setStyleSheet("QHeaderView::section { padding: 8px; font-size: 14px;}")
        checkbox_all = QCheckBox()
        checkbox_all.setChecked(False)
        
        # Create a QWidget to contain the checkbox
        
        widget = QWidget(self.table.horizontalHeader())
        layout = QHBoxLayout(widget)
        widget.setStyleSheet("QWidget { padding-top: 6px; }")
        
        layout.setAlignment(Qt.AlignCenter)  # Center the checkbox
        layout.addWidget(checkbox_all)
        widget.setLayout(layout)

        # Set the widget in the header
        self.table.setCellWidget(0, 0, widget)

        main_layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        h_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addSpacerItem(h_spacer)

        self.add_button = QPushButton("Execute")
        self.add_button.setStyleSheet("QPushButton { background-color: #3498db;color: white;border-radius: 8px;padding: 8px;font-size: 16px;font-weight: bold;border: none; min-width: 120px;}QPushButton:hover {    background-color: #2980b9;}QPushButton:pressed {    background-color: #1c598a;}")
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("QPushButton { background-color: #e74c3c;;color: white;border-radius: 8px;padding: 8px;font-size: 16px;font-weight: bold;border: none; min-width: 120px;}QPushButton:hover {    background-color: #c0392b;}QPushButton:pressed {    background-color: #a93226;}")
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
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""QCheckBox::indicator {    margin-left: 0px;    margin-right: 0px;}QCheckBox {    padding: 0px;    margin: 0px;}""")
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            checkbox_widget.setStyleSheet("QWidget { padding-top: 6px; }")
            self.table.setCellWidget(row, 0, checkbox_widget)

            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("description", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get("price", ""))))
            
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
            self.table.setCellWidget(row, 11, actions_widget)
    
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