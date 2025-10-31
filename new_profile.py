import hashlib
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QMessageBox

from custom_widgets.password_edit import PasswordEdit
from custom_widgets.recommendations import PasswordRecommendations
from ui.new_profile_ui import Ui_MainWindow


class NewProfileWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, authWindow):
        super().__init__()
        self.setupUi(self)
        self.authWindow = authWindow
        self.connection = sqlite3.connect("db.sqlite")
        self.setupWidgets()
        self.enterButton.clicked.connect(self.signUp)

    def setupWidgets(self):
        self.recommendations = PasswordRecommendations()
        self.centralwidget.layout().addWidget(self.recommendations)
        self.passwordEdit = PasswordEdit(self.recommendations, parent=self)
        self.passwordEdit.setFont(self.confirmEdit.font())
        self.loginLayout.addWidget(self.passwordEdit, 1, 1, 1, 1)

        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.setTabOrder(self.loginEdit, self.passwordEdit)
        self.setTabOrder(self.passwordEdit, self.confirmEdit)
        self.setTabOrder(self.confirmEdit, self.enterButton)

        self.loginEdit.setFocus()

    def signUp(self):
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        confirm = self.confirmEdit.text()

        if len(login) == 0 or len(password) == 0:
            self.status.showMessage("Empty login or password", 3000)
        elif len(password) < 5 or len(login) < 3:
            self.status.showMessage("Too short login or password", 3000)
        elif password != confirm:
            self.status.showMessage("The passwords don't match", 3000)
        else:
            user = self.connection.cursor().execute("SELECT username FROM users WHERE username = ?",
                                                    (login,)).fetchall()
            if len(user) > 0:
                self.statusBar().showMessage("This login is already taken", 3000)
            else:
                try:
                    hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    self.connection.cursor().execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                                     (login, hashed))
                    QMessageBox.information(self, "Success", f"Profile for {login} was successfully created")
                    self.connection.commit()
                    self.connection.close()
                    self.close()
                except sqlite3.Error as e:
                    self.status.showMessage(f"{e}", 3000)

    def closeEvent(self, event):
        self.authWindow.show()
        self.deleteLater()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.enterButton.click()
