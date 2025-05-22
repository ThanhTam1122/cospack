import sys
from PySide6.QtWidgets import QApplication
from ui.fee_quote_ui import FeeQuoteUI

def main():
    app = QApplication(sys.argv)
    window = FeeQuoteUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()