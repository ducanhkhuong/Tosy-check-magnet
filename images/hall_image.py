from scanf import scanf
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage , QPainter, QPen, QColor , QBrush ,QFont
import sys
import cv2
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from Serial.serial_hal import SerialReader
from Guider.guider_main import MainWindow
import configparser
import time
from Define.define import Config , Command , Calib , Sensor , Flags , Total
from Config.config import load_config 
from PyQt5.QtGui import QTransform


class ImageWithPoints(QWidget):
    def __init__(self, image_path, *sensor_groups):
        super().__init__()

        self.image_path = image_path
        self.sensor_groups = sensor_groups
        self.rotation = 180

        self.original_pixmap = QPixmap(self.image_path)

        self.pixmap = self.original_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation
        )

        self.sensor_colors = {}
        self.default_color = QColor(255, 0, 0)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel()
        self.draw_points()

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.label_jig_b = QLabel("JigB", self)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)

        self.label_jig_b.setFont(font)
        self.label_jig_b.setStyleSheet("color: white;")
        self.label_jig_b.adjustSize()
        self.label_jig_b.move(23, 15)

        self.label_jig_a = QLabel("JigA", self)
        self.label_jig_a.setFont(font)
        self.label_jig_a.setStyleSheet("color: white;")
        self.label_jig_a.adjustSize()
        self.label_jig_a.move(511, 15)

        self.setWindowTitle("Draw Points on Image")
        self.show()

    def get_color_by_id(self, sensor_id):
        return self.sensor_colors.get(sensor_id, self.default_color)

    def draw_points(self):
        self.pixmap = self.original_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation
        )

        painter = QPainter(self.pixmap)
        radius = 10

        for sensors in self.sensor_groups:
            for s in sensors:
                color = self.get_color_by_id(s.id)
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(color, 2))
                painter.drawEllipse(
                    int(s.x - radius),
                    int(s.y - radius),
                    radius * 2,
                    radius * 2
                )

        painter.end()
        self.label.setPixmap(self.pixmap)

    def set_sensor_color(self, sensor_id, color_name):
        self.sensor_colors[sensor_id] = QColor(color_name)
        self.draw_points()