from scanf import scanf
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QImage
import sys
import cv2
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from Serial.serial_hal import SerialReader
from Guider.guider_main import MainWindow
import configparser
import time
from Define.define import Config , Command , Calib , Sensor , Flags , Total
from Config.config import load_config 

def compare_value_timer(main_window):
    timer = QTimer()
    timer.setInterval(200)
    timer.timeout.connect(lambda: update_compare_values(main_window))
    timer.start()
    main_window.compare_value_timer = timer

def update_compare_values(main_window):
    text1 = main_window.ValueCompare1.text().strip()
    text2 = main_window.ValueCompare2.text().strip()

    if text1.isdigit():
        Command.value_compare_1 = str(int(text1))
        Flags.is_compare1 = True
    else:
        Command.value_compare_1 = "0"
        Flags.is_compare1 = False

    if text2.isdigit():
        Command.value_compare_2 = str(int(text2))
        Flags.is_compare2 = True
    else:
        Command.value_compare_2 = "0"
        Flags.is_compare2 = False
