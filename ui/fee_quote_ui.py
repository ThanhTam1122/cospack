from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox

class FeeQuoteUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("運送会社料金見積")
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Horizontal layout for total inputs
        total_inputs_layout = QHBoxLayout()

        # 合計個口数
        total_num_layout = QVBoxLayout()
        total_num_label = QLabel("合計個口数")
        self.total_num_edit = QLineEdit()
        self.total_num_edit.setPlaceholderText("例: 5")
        total_num_layout.addWidget(total_num_label)
        total_num_layout.addWidget(self.total_num_edit)

        # 合計才数
        total_volume_layout = QVBoxLayout()
        total_volume_label = QLabel("合計才数")
        self.total_volume_edit = QLineEdit()
        self.total_volume_edit.setPlaceholderText("例: 3.5")
        total_volume_layout.addWidget(total_volume_label)
        total_volume_layout.addWidget(self.total_volume_edit)

        # 合計重量
        total_weight_layout = QVBoxLayout()
        total_weight_label = QLabel("合計重量 (kg)")
        self.total_weight_edit = QLineEdit()
        self.total_weight_edit.setPlaceholderText("例: 50")
        total_weight_layout.addWidget(total_weight_label)
        total_weight_layout.addWidget(self.total_weight_edit)

        # 郵便番号
        postal_layout = QVBoxLayout()
        postal_label = QLabel("郵便番号")
        self.postal_edit = QLineEdit()
        self.postal_edit.setPlaceholderText("例: 1234567")
        postal_layout.addWidget(postal_label)
        postal_layout.addWidget(self.postal_edit)

        # Calculate button(料金を計算)
        calc_layout = QVBoxLayout()
        calc_label = QLabel("")
        self.calc_button = QPushButton("料金を計算")
        calc_layout.addWidget(calc_label)
        calc_layout.addWidget(self.calc_button)
        

        # Add all to the horizontal layout
        total_inputs_layout.addLayout(total_num_layout)
        total_inputs_layout.addLayout(total_volume_layout)
        total_inputs_layout.addLayout(total_weight_layout)
        total_inputs_layout.addLayout(postal_layout)
        total_inputs_layout.addLayout(calc_layout)

        # Add to main layout
        main_layout.addLayout(total_inputs_layout)
        
        # Detail input
        self.detail_groupbox = QGroupBox("詳細入力")
        self.detail_layout = QVBoxLayout()
        self.add_item_row()
        self.detail_groupbox.setLayout(self.detail_layout)
        main_layout.addWidget(self.detail_groupbox)

        self.add_item_button = QPushButton("+ 荷物追加")
        main_layout.addWidget(self.add_item_button)

        self.setLayout(main_layout)

        self.add_item_button.clicked.connect(self.add_item_row)

    def add_item_row(self):
        # Create a horizontal layout for a new row
        row_layout = QHBoxLayout()
        
        size_edit = QLineEdit()
        size_edit.setPlaceholderText("サイズ (cm)")
        
        weight_edit = QLineEdit()
        weight_edit.setPlaceholderText("重量 (kg)")
        
        x_label = QLabel(" x ")
        
        quantity_edit = QLineEdit()
        quantity_edit.setPlaceholderText("個口数")
        
        #Use a local variable for the delete button
        del_button = QPushButton("X")
        del_button.clicked.connect(lambda: self.remove_item_row(row_layout))

        #Add widgets to the row
        row_layout.addWidget(size_edit)
        row_layout.addWidget(weight_edit)
        row_layout.addWidget(x_label)
        row_layout.addWidget(quantity_edit)
        row_layout.addWidget(del_button)

        #Keep track of the row layout so we can remove it
        self.detail_layout.addLayout(row_layout)

    def remove_item_row(self, layout):
        # Remove all widgets in the row layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Remove the layout itself from the parent layout
        self.detail_layout.removeItem(layout)