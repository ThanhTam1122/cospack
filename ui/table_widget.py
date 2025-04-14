from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

class TableWidget(QTableWidget):
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self.init_ui()

    def init_ui(self):
        # Set default properties for the table widget
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["", "出荷日付", "ピッキング連番", "ピッキング日", "ピッキング時刻", "受注No_From", "受注No_To", "得意先CD_From", "得意先CD_To", "得意先略称", "担当者CD", "担当者略称"])
        # self.table.horizontalHeader().setSectionResizeMode(11, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 20)  # First column (checkbox)
        self.table.setStyleSheet("QHeaderView::section { padding: 8px; padding-left: 10px; font-size: 14px;}")
        # checkbox_all = QCheckBox()
        # checkbox_all.setChecked(False)
        # checkbox_all.stateChanged.connect(self.toggle_select_all)
        # # Create a QWidget to contain the checkbox
        
        # widget = QWidget(self.table.horizontalHeader())
        # layout = QHBoxLayout(widget)
        # widget.setStyleSheet("QWidget { padding-top: 6px; }")
        
        # layout.setAlignment(Qt.AlignCenter)  # Center the checkbox
        # layout.addWidget(checkbox_all)
        # widget.setLayout(layout)

        # Set the widget in the header
        # self.table.setCellWidget(0, 0, widget)

    def set_headers(self, headers):
        """Set the headers for the table."""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def add_row(self, row_data):
        """Add a row to the table."""
        row = self.rowCount()
        self.insertRow(row)
        for column, data in enumerate(row_data):
            self.setItem(row, column, QTableWidgetItem(str(data)))

    def clear_table(self):
        """Clear all rows from the table."""
        self.setRowCount(0)