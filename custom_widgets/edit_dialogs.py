from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit

import restrictions
from custom_widgets.password_edit import PasswordEdit
from custom_widgets.recommendations import PasswordRecommendations


class ServiceDialog(QDialog):
    def __init__(self, values=None):
        super().__init__()
        self.setModal(True)
        layout = QFormLayout()
        if values is None:
            values = [""] * 2
            self.setWindowTitle("New service")
        else:
            self.setWindowTitle("Edit service")

        self.name = QLineEdit(values[0])
        self.name.setMaxLength(restrictions.name)
        self.address = QLineEdit(values[1])
        self.address.setMaxLength(restrictions.address)
        layout.addRow("Service", self.name)
        layout.addRow("Address", self.address)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

    def getData(self):
        return self.name.text(), self.address.text()


class AccountDialog(QDialog):
    def __init__(self, values=None):
        super().__init__()
        self.setModal(True)
        layout = QFormLayout()
        if values is None:
            values = [""] * 3
            self.setWindowTitle("New account")
        else:
            self.setWindowTitle("Edit account")

        self.recommendations = PasswordRecommendations()
        self.logins = QLineEdit(values[0])
        self.logins.setMaxLength(restrictions.logins)
        self.password = PasswordEdit(self.recommendations)
        self.password.setText(values[1])
        self.commentary = QLineEdit(values[2])
        self.commentary.setMaxLength(restrictions.commentary)
        layout.addRow("Commentary", self.commentary)
        layout.addRow("Logins (separated by ;)", self.logins)
        layout.addRow("Password", self.password)
        layout.addRow(self.recommendations)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

    def getData(self):
        return self.logins.text(), self.password.text(), self.commentary.text()