from PySide6.QtWidgets import ( QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCheckBox, QWidget, QHBoxLayout )
from PySide6.QtCore import Qt, QRect, Signal

class TableWidget(QTableWidget):
    
    selection_updated = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.total_count = 0
        self.selected_count = 0
        self.selected_items = {}
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(13)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setHorizontalHeaderLabels(["","ID", "出荷日付", "ピッキング連番", "ピッキング日", "ピッキング時刻", "受注No_From", "受注No_To", "得意先CD_From", "得意先CD_To", "得意先略称", "担当者CD", "担当者略称"])
        self.horizontalHeader().setSectionResizeMode(12, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(11, QHeaderView.ResizeToContents)
        self.setColumnWidth(0, 40)  # First column (checkbox)
        self.setColumnHidden(1, True)
        self.setStyleSheet("QHeaderView::section { padding: 8px; font-size: 14px;}")
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.clicked.connect(self.on_row_click)

        self.checkbox_all = QCheckBox()
        self.checkbox_all.setChecked(False)
        self.checkbox_all.clicked.connect(self.toggle_select_all)
        
        widget=QWidget(self.horizontalHeader())
        widget.setGeometry(QRect(0, 0, 38, 40))
        layout=QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)  # Center the checkbox
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox_all)
        widget.setLayout(layout)
        self.setCellWidget(0, 0, widget)

    def update_table(self, items, total_count):
        self.total_count = total_count
        self.setRowCount(0)
        self.checkbox_all.setChecked(True)
        for row, item in enumerate(items):
            self.insertRow(row)
            
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox.clicked.connect(self.on_checkbox_clicked)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.setCellWidget(row, 0, checkbox_widget)
            self.setItem(row, 1, QTableWidgetItem(str(item.get("picking_id", ""))))
            self.setItem(row, 2, QTableWidgetItem(str(item.get("picking_date", ""))))
            self.setItem(row, 3, QTableWidgetItem(str(item.get("picking_time", ""))))
            self.setItem(row, 4, QTableWidgetItem(str(item.get("shipping_date", ""))))
            self.setItem(row, 5, QTableWidgetItem(str(item.get("order_no_from", ""))))
            self.setItem(row, 6, QTableWidgetItem(str(item.get("order_no_to", ""))))
            self.setItem(row, 7, QTableWidgetItem(str(item.get("customer_code_from", ""))))
            self.setItem(row, 8, QTableWidgetItem(str(item.get("customer_code_to", ""))))
            self.setItem(row, 9, QTableWidgetItem(str(item.get("customer_short_name", ""))))
            self.setItem(row, 10, QTableWidgetItem(str(item.get("staff_code", ""))))
            self.setItem(row, 11, QTableWidgetItem(str(item.get("staff_short_name", ""))))
            self.setItem(row, 12, QTableWidgetItem(""))

            picking_id = str(item.get("picking_id", ""))
            if picking_id in self.selected_items and self.selected_items[picking_id] == 1:
                checkbox.setChecked(True)
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(True)
            else:
                self.checkbox_all.setChecked(False)

        self.update_selected_count()

    def on_checkbox_clicked(self):
        self.update_selection()

    def on_row_click(self, item):
        row = item.row()
        checkbox = self.cellWidget(row, 0).findChild(QCheckBox)
        if checkbox and checkbox.isChecked():
            checkbox.setChecked(False)
        else:
            checkbox.setChecked(True)

        self.update_selection()

    def toggle_select_all(self):
        state = self.checkbox_all.checkState()

        for row in range(self.rowCount()):
            item = self.cellWidget(row, 0).findChild(QCheckBox)
            if item:
                item.setChecked(state == Qt.Checked)

            if state == Qt.Checked:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(True)
                        self.selected_items[self.item(row, 1).text()] = 1
            else:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(False)
                        self.selected_items[self.item(row, 1).text()] = 0
        self.update_selected_count()

    def update_selection (self):
        for row in range(self.rowCount()):
            checkbox = self.cellWidget(row, 0).findChild(QCheckBox)

            if checkbox and checkbox.isChecked():
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(True)
                        self.selected_items[self.item(row, 1).text()] = 1
            else:
                for i in range(self.columnCount()):
                    item = self.item(row, i)
                    if item:
                        item.setSelected(False)
                        self.selected_items[self.item(row, 1).text()] = 0
        
        self.update_selected_count()

    def update_selected_count (self):
        self.selected_count = 0
        for key in self.selected_items.keys():
            if self.selected_items[key] == 1:
                self.selected_count += 1

        self.selection_updated.emit(self.total_count, self.selected_count)

    def get_selected_items(self):
        result = []
        for key in self.selected_items.keys():
            if self.selected_items[key] == 1:
                result.append(key)
        return result

    def remove_pickings(self, pickings):
        """Remove pickings from the table."""
        for picking in pickings:
            self.selected_items[str(picking['picking_id'])] = -1

    def clear_table(self):
        """Clear all rows from the table."""
        self.setRowCount(0)
