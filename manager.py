import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QMenu, QLineEdit, QMessageBox, \
    QTableView, QDialog, QStyledItemDelegate

import cipher
import restrictions
from custom_widgets.edit_dialogs import AccountDialog, ServiceDialog
from ui.manager_ui import Ui_MainWindow


class ManagerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, authWindow, userId: int, login: str, key: str):
        super().__init__()
        self.setupUi(self)
        self.selectedTable = None
        self.selectedRow = None
        self.selectedService = None
        self.selectedAccount = None
        self.authWindow = authWindow
        self.userId = userId
        self.key = key
        self.setWindowTitle(f"Another password manager - {login}")
        self.connection = sqlite3.connect("db.sqlite")
        self.initTables()
        self.refillServices()
        self.updateSelection(self.servicesColumn)
        self.setupActions()

    def setupActions(self):
        separator = QAction(self)
        separator.setSeparator(True)

        serviceMenu = QMenu()
        serviceMenu.addActions([self.newServiceAction, separator, self.editAction, self.deleteAction])
        self.servicesColumn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        (self.servicesColumn.customContextMenuRequested
         .connect(lambda position: serviceMenu.exec(self.servicesColumn.viewport().mapToGlobal(position))))

        accountMenu = QMenu()
        accountMenu.addActions([self.newAcoountAction, separator, self.editAction, self.deleteAction])
        self.accountsColumn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        (self.accountsColumn.customContextMenuRequested
         .connect(lambda position: accountMenu.exec(self.accountsColumn.viewport().mapToGlobal(position))))

        self.logoutAction.triggered.connect(self.logout)
        self.newServiceAction.triggered.connect(lambda: self.editService(1))
        self.newAcoountAction.triggered.connect(lambda: self.editAccount(1))
        (self.editAction.triggered.connect
         (lambda: self.editService(0) if self.selectedTable == self.servicesColumn else self.editAccount(0)))
        (self.deleteAction.triggered.connect
         (lambda: self.deleteService() if self.selectedTable == self.servicesColumn else self.deleteAccount()))

        self.editAction.setShortcut(QKeySequence("F2"))
        self.deleteAction.setShortcut(QKeySequence("Del"))
        self.newAcoountAction.setShortcut(QKeySequence("Ctrl+N"))
        self.newServiceAction.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self.logoutAction.setShortcut(QKeySequence("ESC"))

    def initTables(self):
        cursor = self.connection.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS services (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT({restrictions.name}) NOT NULL,
                        address TEXT({restrictions.address}),
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        )""")
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        logins TEXT({restrictions.logins}) NOT NULL,
                        password TEXT NOT NULL,
                        commentary TEXT({restrictions.commentary}),
                        service_id INTEGER NOT NULL,
                        FOREIGN KEY (service_id) REFERENCES services(id)
                        );""")
        self.connection.commit()

        for table in self.servicesColumn, self.accountsColumn:
            table.setItemDelegate(ReadOnlyDelegate())
            table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            table.verticalHeader().setVisible(False)

    def updateTable(self, table: QTableView):
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.selectionModel().selectionChanged.connect(lambda: self.updateSelection(table))

    def refillServices(self):
        model = QStandardItemModel()
        cursor = self.connection.cursor()
        data = cursor.execute("SELECT id, name, address FROM services WHERE user_id = ?",
                              (self.userId,)).fetchall()
        for i, row in enumerate(data):
            model.appendRow([QStandardItem(str(item)) for item in row])
        model.setHorizontalHeaderLabels([str(item[0]) for item in cursor.description])
        self.servicesColumn.setModel(model)
        self.servicesColumn.selectionModel().selectionChanged.connect(lambda: self.updateSelection(self.servicesColumn))
        self.updateTable(self.servicesColumn)

    def refillAccounts(self):
        model = QStandardItemModel()
        cursor = self.connection.cursor()
        data = cursor.execute("SELECT id, logins, password, commentary FROM accounts WHERE service_id = ?",
                                  (self.selectedService,)).fetchall()
        for i, row in enumerate(data):
            row = list(row)
            row[1] = "\n".join(str(row[1]).split(";"))
            row[2] = cipher.decrypt(row[2], self.key)
            model.appendRow([QStandardItem(str(item)) for item in row])
        model.setHorizontalHeaderLabels([str(item[0]) for item in cursor.description])
        self.accountsColumn.setModel(model)
        self.accountsColumn.selectionModel().selectionChanged.connect(lambda: self.updateSelection(self.accountsColumn))
        self.updateTable(self.accountsColumn)

    def updateSelection(self, table: QTableView):
        self.selectedTable = table
        selected = table.selectionModel().selectedIndexes()
        if len(selected) == 0:
            self.selectedRow = None
            selectedId = -1
            self.editAction.setDisabled(True)
            self.deleteAction.setDisabled(True)
        else:
            self.selectedRow = selected[0].row()
            selectedId = int(table.model().item(self.selectedRow, 0).text())
            self.editAction.setDisabled(False)
            self.deleteAction.setDisabled(False)

        if table == self.servicesColumn:
            self.selectedService = selectedId
            self.refillAccounts()
            if self.selectedService == -1:
                self.newAcoountAction.setDisabled(True)
            else:
                self.newAcoountAction.setDisabled(False)
        elif table == self.accountsColumn:
            self.selectedAccount = selectedId

    def editService(self, mode: int):
        model = self.servicesColumn.model()
        values = [""] * 2 if mode else [model.item(self.selectedRow, i).text() for i in (1, 2)]
        title = "New service" if mode else "Edit service"
        query = "INSERT INTO services (name, address, user_id) VALUES (?, ?, ?)" if mode else \
            "UPDATE services SET name = ?, address = ? WHERE id = ?"

        dialog = ServiceDialog(values)
        dialog.setWindowTitle(title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, address = dialog.getData()
            if len(name) > restrictions.name:
                QMessageBox.critical(self, "Error", f"Service name length should be less than {restrictions.name}")
            elif len(name) == 0:
                QMessageBox.critical(self, "Error", f"Service name is empty")
            elif len(address) > restrictions.address:
                QMessageBox.critical(self, "Error", f"Service adrress length should be less than {restrictions.address}")
            else:
                queryValues = (name, address, self.userId if mode else self.selectedService)
                self.connection.cursor().execute(query,queryValues)
                self.connection.commit()
                self.refillServices()

    def editAccount(self, mode: int):
        model = self.accountsColumn.model()
        values = [""] * 3 if mode else [model.item(self.selectedRow, i).text() for i in (1, 2, 3)]
        values[0] = ";".join(values[0].splitlines())
        title = "New account" if mode else "Edit account"
        query = "INSERT INTO accounts (logins, password, commentary, service_id) VALUES (?, ?, ?, ?)" if mode else \
            "UPDATE accounts SET logins = ?, password = ?, commentary = ? WHERE id = ?"

        dialog = AccountDialog(values)
        dialog.setWindowTitle(title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            logins, password, commentary = dialog.getData()
            if len(logins) == 0:
                QMessageBox.critical(self, "Error", f"Logins are empty")
            elif len(password) == 0:
                QMessageBox.critical(self, "Error", f"Password is empty")
            else:
                encrypted = cipher.encrypt(password, self.key)
                queryValues = (logins, encrypted, commentary, self.selectedService if mode else self.selectedAccount)
                self.connection.cursor().execute(query, queryValues)
                self.connection.commit()
                self.refillAccounts()

    def deleteService(self):
        reply = (QMessageBox.question(self, "Warning", f"Do you really want to delete "
                                        f"{self.servicesColumn.model().item(self.selectedRow, 1).text()}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No))
        if reply == QMessageBox.StandardButton.Yes:
            self.connection.cursor().execute(f"DELETE FROM services WHERE id = ?",
                                             (self.selectedService, ))
            self.connection.commit()
            self.refillServices()

    def deleteAccount(self):
        reply = (QMessageBox.question(self, "Warning", f"Do you really want to delete this account?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No))
        if reply == QMessageBox.StandardButton.Yes:
            self.connection.cursor().execute(f"DELETE FROM accounts WHERE id = ?",
                                             (self.selectedAccount, ))
            self.connection.commit()
            self.refillAccounts()

    def logout(self):
        self.connection.close()
        self.authWindow.connection = sqlite3.connect("db.sqlite")
        self.authWindow.show()
        self.close()
        self.deleteLater()

class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor