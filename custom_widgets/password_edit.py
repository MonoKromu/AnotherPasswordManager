from PyQt6.QtCore import QRegularExpression
from PyQt6.QtWidgets import QLineEdit

from custom_widgets.recommendations import PasswordRecommendations


class PasswordEdit(QLineEdit):
    def __init__(self, widget: PasswordRecommendations, baseText=None, parent=None):
        super().__init__(baseText, parent)
        self.widget = widget
        self.textChanged.connect(self.checkPassword)
        self.dReg = QRegularExpression("\\d")
        self.sReg = QRegularExpression("[^a-zA-Z0-9]")
        self.common = []
        with open("custom_widgets/common_password.txt", "r", encoding='utf-8') as file:
            self.common = file.read().splitlines()

    def checkPassword(self):
        text = self.text()
        checks = [len(text) > 8,
                  text.lower() != text and text.upper() != text,
                  self.dReg.match(text).hasMatch(),
                  self.sReg.match(text).hasMatch(),
                  text not in self.common and len(text) > 0]
        for key, value in zip(self.widget.recoms.keys(), checks):
            self.widget.setFit(key, value)
        self.widget.setStrength(sum([int(value) * 20 for value in checks]))
