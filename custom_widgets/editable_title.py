from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QMouseEvent, QFont
from PyQt6.QtWidgets import QLabel, QFileDialog, QSizePolicy
import os
import shutil


class EditableTitle(QLabel):
    def __init__(self, text, parent=None):
        self.baseText = text
        super().__init__(text, parent)
        self.setFont(QFont("Tahoma", 30))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumSize(self.width(), self.height())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.changePicture("logo")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            path, _ = QFileDialog.getOpenFileName(self, "Choose image", "",
                                                  "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
            if path != "":
                self.saveImage(path)
                self.changePicture(path)
        else:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.changePicture("")

    def saveImage(self, path):
        try:
            logo_path = os.path.join(os.getcwd(), "logo")
            shutil.copy2(path, logo_path)
        except Exception as e:
            print(f"{e}")

    def deleteImage(self):
        try:
            path = os.path.join(os.getcwd(), "logo")
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Ошибка при удалении файла logo: {e}")

    def changePicture(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(pixmap)
        else:
            self.clear()
            self.setText(self.baseText)
            self.deleteImage()

    def resizeEvent(self, event):
        pixmap = QPixmap("logo")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self.setPixmap(pixmap)