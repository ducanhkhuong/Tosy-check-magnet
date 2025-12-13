from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMessageBox
import sys
import os
from PyQt5 import uic
from Config.config import load_config , get_resource_path

class MainWindow(QtWidgets.QMainWindow):     # MainWindow class with parent is QtWidgets.QMainWindow
    # Constructor
    def __init__(self, *args, **kwargs):
        # Call the init of the parents, super() do not need arguments in python3
        super().__init__(*args, **kwargs)
        # Load the UI Page
        ui_path = get_resource_path("Guider/hall_array.ui")
        uic.loadUi(ui_path, self)
        #uic.loadUi('Guider/hall_array.ui', self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showMinimized()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Thoát chương trình?",
            "Bạn có chắc muốn thoát không?",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
