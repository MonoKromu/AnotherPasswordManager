import hashlib
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMainWindow, QLineEdit

import restrictions
from custom_widgets.editable_title import EditableTitle
from manager import ManagerWindow
from new_profile import NewProfileWindow
from ui.auth_ui import Ui_MainWindow


class AuthenticationWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("db.sqlite")
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordEdit.setMaxLength(30)
        self.loginEdit.setMaxLength(20)
        self.enterButton.clicked.connect(self.signIn)
        self.newButton.clicked.connect(self.signUp)
        self.createTable()
        self.centralwidget.layout().replaceWidget(self.title, EditableTitle("Another Password Manager", self))
        self.title.deleteLater()
        self.repaint()

    def createTable(self):
        self.connection.cursor().execute(f"CREATE TABLE IF NOT EXISTS users("
                                         "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                                         f"username TEXT({restrictions.username}) UNIQUE NOT NULL, "
                                         "password TEXT NOT NULL)")
        self.connection.commit()

    def signIn(self):
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        if len(login) == 0 or len(password) == 0:
            self.status.showMessage("Empty login or password", 3000)
        else:
            hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
            user = self.connection.cursor().execute("SELECT id "
                                                    "FROM users "
                                                    "WHERE username = ? AND password = ?",
                                                    (login, hashed)).fetchall()
            if len(user) == 0:
                self.statusBar().showMessage("Wrong username or password", 3000)
            else:
                self.connection.close()
                userId = user[0][0]
                self.manager = ManagerWindow(self, userId, login, hashed)
                self.manager.show()
                self.hide()
                self.loginEdit.clear()
                self.passwordEdit.clear()


    def signUp(self):
        self.profile = NewProfileWindow(self)
        self.profile.show()
        self.hide()
        self.loginEdit.clear()
        self.passwordEdit.clear()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.enterButton.click()
