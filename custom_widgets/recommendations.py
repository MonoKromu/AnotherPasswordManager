from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QLabel, QProgressBar


class PasswordRecommendations(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recoms = {}
        self.setup()

    def setup(self):
        gridLayout = QtWidgets.QGridLayout(self)
        self.strengthBar = QProgressBar()
        self.strengthBar.setTextVisible(False)
        self.strengthBar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        self.strengthBar.setValue(0)
        mainLabel = QLabel("Password recommendations:", self)
        titles = ["✘More than 8 characters",
                  "✘Upper and lower case letters",
                  "✘Digits",
                  "✘Contains special characters",
                  "✘Not common password"]
        labels = [QLabel(title, self) for title in titles]
        short_titles = ["chars", "letters", "digits", "special", "not_common"]
        self.recoms = dict(zip(short_titles, labels))

        for i, label in enumerate([mainLabel] + labels + [self.strengthBar]):
            gridLayout.addWidget(label, i, 0, 1, 1)
        self.setLayout(gridLayout)

    def setFit(self, prop: str, fit: bool):
        character = "✔" if fit else "✘"
        if self.recoms.get(prop, None) is not None:
            text = self.recoms.get(prop).text()
            text = f"{character}{text[1:]}"
            self.recoms[prop].setText(text)

    def setStrength(self, value: int):
        self.strengthBar.setValue(value)
