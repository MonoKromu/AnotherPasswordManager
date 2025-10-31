import sys

from PyQt6.QtWidgets import QApplication

from auth import AuthenticationWindow

app = QApplication(sys.argv)
ex = AuthenticationWindow()
ex.show()
sys.exit(app.exec())