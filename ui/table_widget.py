from PySide6.QtWidgets import ( QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCheckBox, QWidget, QHBoxLayout, QVBoxLayout )
from PySide6.QtCore import Qt, QRect, Signal

class TableWidget(QTableWidget):
    
    selection_updated = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.row_count = 0
        self.selected_count = 0
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(13)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setHorizontalHeaderLabels(["","Id", "出荷日付", "ピッキング連番", "ピッキング日", "ピッキング時刻", "受注No_From", "受注No_To", "得意先CD_From", "得意先CD_To", "得意先略称", "担当者CD", "担当者略称"])
        self.horizontalHeader().setSectionResizeMode(12, QHeaderView.Stretch)
        self.setColumnWidth(0, 40)  # First column (checkbox)
        self.setColumnHidden(1, True)
        self.setStyleSheet("QHeaderView::section { padding: 8px; padding-left: 10px; font-size: 14px;}")
        self.clicked.connect(self.on_row_click)

        checkbox_all = QCheckBox()
        checkbox_all.setChecked(False)
        checkbox_all.stateChanged.connect(self.toggle_select_all)
        widget = QWidget(self.horizontalHeader())
        widget.setGeometry(QRect(0, 0, 38, 40))
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)  # Center the checkbox
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(checkbox_all)
        widget.setLayout(layout)
        self.setCellWidget(0, 0, widget)

    def update_table(self, items):
        self.row_count = len(items)
        self.selection_updated.emit(self.row_count, self.selected_count)
        for row, item in enumerate(items):
            self.insertRow(row)
            
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox.clicked.connect(lambda i=item: self.on_checkbox_clicked(i))
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.setCellWidget(row, 0, checkbox_widget)

            self.setItem(row, 1, QTableWidgetItem(str(item.get("picking_id", ""))))
            self.setItem(row, 2, QTableWidgetItem(str(item.get("picking_date", ""))))
            self.setItem(row, 3, QTableWidgetItem(item.get("picking_time", "")))
            self.setItem(row, 4, QTableWidgetItem(item.get("shipping_date", "")))
            self.setItem(row, 5, QTableWidgetItem(str(item.get("order_no_from", ""))))
            self.setItem(row, 6, QTableWidgetItem(str(item.get("order_no_to", ""))))
            self.setItem(row, 7, QTableWidgetItem(str(item.get("customer_code_from", ""))))
            self.setItem(row, 8, QTableWidgetItem(str(item.get("customer_code_to", ""))))
            self.setItem(row, 9, QTableWidgetItem(str(item.get("customer_short_name", ""))))
            self.setItem(row, 10, QTableWidgetItem(str(item.get("staff_code", ""))))
            self.setItem(row, 11, QTableWidgetItem(str(item.get("staff_short_name", ""))))
            self.setItem(row, 12, QTableWidgetItem(""))

    def on_checkbox_clicked(self, item):
        self.update_selected_row_count()

    def on_row_click(self, index):
        row = index.row()
        checkbox = self.cellWidget(row, 0).findChild(QCheckBox)
        if checkbox and checkbox.isChecked():
            checkbox.setChecked(False)
        else:
            checkbox.setChecked(True)
        self.update_selected_row_count()

    def toggle_select_all(self, state):
        if state == 2:
            self.selected_count = self.rowCount()
        else:
            self.selected_count = 0
        self.selection_updated.emit(self.row_count, self.selected_count)

        for row in range(self.rowCount()):
            item = self.cellWidget(row, 0).findChild(QCheckBox)
            if item:
                item.setChecked(1 if state == 2 else 0)

            if state == 2:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(True)
            else:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(False)

    def update_selected_row_count (self):
        selected_count = 0
        for row in range(self.rowCount()):
            checkbox = self.cellWidget(row, 0).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                selected_count += 1
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(True)
            else:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(False)
        self.selected_count = selected_count
        self.selection_updated.emit(self.row_count, self.selected_count)

    def clear_table(self):
        """Clear all rows from the table."""
        self.setRowCount(0)
