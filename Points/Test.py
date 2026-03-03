import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QTransform
from PyQt5.QtCore import Qt

IMAGE_PATH = "/home/rpi/python_ws/HallArrayViewer/Points/image.png"
OUTPUT_JSON = "points.json"


class ImageWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load ảnh và xoay 180 độ mặc định
        self.pix = QPixmap(IMAGE_PATH)

        self.setPixmap(self.pix)

        self.points = []
        self.collecting = False

    def start_collect(self):
        self.collecting = True
        self.points = []
        self.setPixmap(self.pix.copy())

    def stop_collect(self):
        self.collecting = False
        with open(OUTPUT_JSON, "w") as f:
            json.dump(
                [{"x": p.x(), "y": p.y()} for p in self.points],
                f,
                indent=4
            )
        print(f"Đã lưu {len(self.points)} điểm vào {OUTPUT_JSON}")

    def mousePressEvent(self, event):
        if self.collecting and event.button() == Qt.LeftButton:
            pos = event.pos()
            self.points.append(pos)
            print("Clicked:", pos.x(), pos.y())


            pixmap_copy = self.pixmap().copy()
            painter = QPainter(pixmap_copy)
            painter.setPen(QPen(Qt.red, 6))
            painter.drawPoint(pos)
            painter.end()

            self.setPixmap(pixmap_copy)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Point Collector - PyQt5")

        self.image_widget = ImageWidget()

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.image_widget.start_collect)

        self.btn_stop = QPushButton("Stop & Save")
        self.btn_stop.clicked.connect(self.image_widget.stop_collect)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.resize(
            self.image_widget.pix.width(),
            self.image_widget.pix.height() + 50
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
