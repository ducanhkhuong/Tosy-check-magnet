from scanf import scanf
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QImage , QPainter, QPen, QColor
import sys
import cv2
import re
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from Serial.serial_hal import SerialReader
from Guider.guider_main import MainWindow
import configparser
import time
from Define.define import Config , Command , Calib , Sensor , Flags , Total
from Config.config import load_config , get_resource_path
from Timer.compare_value import compare_value_timer
from images.hall_image import ImageWithPoints
from Log.logger import Logger
import subprocess

serial_reader = None
total = Total()
CURRENT_CUBE = "Cube20"
cfg = None

def main(cfg_input, logger):
    global cfg
    cfg = cfg_input
    logger.info("\nApplication open")
    logger.info("Load configfile : done")
    logger.info(f"Port={cfg.port}, Baudrate={cfg.baudrate}")

    #init Guider
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    design_width = main_window.width()
    design_height = main_window.height()
    logger.info(f"UI Designer size y={design_width},x={design_height}")
    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    scale = dpi / 96
    logger.info(f"DPI ={dpi},Scale ={scale}")
    logger.info("Load Screen : done")
    scaled_width = int(design_width * scale)
    scaled_height = int(design_height * scale)
    main_window.resize(scaled_width, scaled_height)
    main_window.setMinimumSize(scaled_width, scaled_height)
    main_window.setMaximumSize(scaled_width, scaled_height)

    #Set default values
    main_window.labelDeviceStatus.setText("Device not connected")
    main_window.linePort.setText(cfg.port)
    main_window.lineBaudrate.setText(cfg.baudrate)
    main_window.ColorConnect.setText("")
    main_window.ColorConnect.setStyleSheet("background-color: red")
    main_window.ColorCl1.setText("")
    main_window.ColorCl1.setStyleSheet("background-color: red")
    main_window.ColorCl2.setText("")
    main_window.ColorCl2.setStyleSheet("background-color: red")
    main_window.ColorCheck1.setText("")
    main_window.ColorCheck1.setStyleSheet("background-color: red")
    main_window.ColorCheck2.setText("")
    main_window.ColorCheck2.setStyleSheet("background-color: red")

    #Debug
    def open_debug_terminal():
        subprocess.Popen([
            "lxterminal",
            "-e",
            "bash -c 'tail -f /home/rpi/Application/log/hall_array_viewer.log; exec bash'"
        ])

    #Initial load image
    image = None

    def load_image_from_config():
        nonlocal image

        if image:
            image.deleteLater()

        image_path = get_resource_path(cfg.image)

        rotation = 0
        if "cube20" in cfg.image.lower():
            rotation = 180

        sensors_a = cfg.calib["Calib1"].sensors[rotation]
        sensors_b = cfg.calib["Calib2"].sensors[rotation]

        image = ImageWithPoints(
            image_path,
            sensors_a,
            sensors_b,
            rotation
        )

        image.sensor_colors = {}
        image.draw_points()

        logger.info(f"Load image: {cfg.image}")

    load_image_from_config()

    def switch_cube():
        global cfg, CURRENT_CUBE
        if CURRENT_CUBE == "Cube20":
            cfg_path = get_resource_path("Config/config_cube16l.json")
            CURRENT_CUBE = "Cube16"
        else:
            cfg_path = get_resource_path("Config/config_cube20l.json")
            CURRENT_CUBE = "Cube20"
        logger.info(f"Switch cube -> {CURRENT_CUBE}")

        cfg = load_config(cfg_path)
        main_window.linePort.setText(cfg.port)
        main_window.lineBaudrate.setText(cfg.baudrate)
        main_window.btnImage.setText(CURRENT_CUBE)
        load_image_from_config()

    #Button Debug
    main_window.btnDebug.clicked.connect(open_debug_terminal)

    #Button Rotate
    main_window.btnRotate.clicked.connect(lambda: image.rotate_180(cfg))

    #Button Switch Cube
    main_window.btnImage.setText("Cube20")
    main_window.btnImage.clicked.connect(switch_cube)

    #Button Connect/Disconnect
    main_window.buttonConnect.setText("Connect")
    main_window.buttonConnect.clicked.connect(lambda: button_connect_click())

    def update_ui_connected(state):
        Flags.is_connected = state
        if state:
            main_window.labelDeviceStatus.setText("COM Port connected")
            main_window.ColorConnect.setStyleSheet("background-color: green")
            main_window.buttonConnect.setText("Disconnect")
            logger.info("Connect : Connected open")

        else:
            main_window.labelDeviceStatus.setText("COM Port disconnected")
            main_window.ColorConnect.setStyleSheet("background-color: red")
            main_window.buttonConnect.setText("Connect")

    def on_serial_connected():
        update_ui_connected(True)


    def on_serial_disconnected():
        update_ui_connected(False)
        logger.warning("Serial lost - reconnecting...")

    def button_connect_click():
        global serial_reader
        if serial_reader is None:
            comport = main_window.linePort.text()
            serial_reader = SerialReader(comport)
            serial_reader.data_received.connect(process_serial_data)
            serial_reader.connected.connect(on_serial_connected)
            serial_reader.disconnected.connect(on_serial_disconnected)
            serial_reader.connect_port()
            main_window.labelDeviceStatus.setText("Connecting...")
            logger.info("Connect : Opening")

        else:
            serial_reader.close()
            serial_reader = None
            update_ui_connected(False)
            logger.info("Connect : Connected closed")

    def process_serial_data(data):
        logger.info(f"Reciever : {data}")
        lines = data.strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"(MANUAL|AUTO)(\d):\s*(.*)", line)
            if not match:
                continue

            #parse command
            data_type = match.group(1)

            #parse id
            group_id = int(match.group(2))

            #parse value
            values_str = match.group(3)
            values = []
            for v in values_str.split(","):
                v = v.strip()
                if v in ("0", "1"):
                    values.append(int(v))
                else:
                    logger.warning("Skipping invalid value")
                    continue

            #check sensor number
            N1_S = len(image.sensor_groups[0])
            N2_S = len(image.sensor_groups[1])

            if data_type in ("MANUAL", "AUTO") and group_id == 1:
                if len(values) != N1_S:
                    return

            if data_type in ("MANUAL", "AUTO") and group_id == 2:
                if len(values) != N2_S:
                    return

            #check command
            if data_type == "MANUAL" and Flags.onclick_mode:
                if group_id == 1:                
                    total.list_false_sensors_calib1 = []
                    total.list_done_sensors_calib1 = []
                    #check value
                    for i, val in enumerate(values):
                        if val == 1:
                            total.list_false_sensors_calib1.append(i)
                        else:
                            total.list_done_sensors_calib1.append(i)
                    #check passed/fail
                    if all(v == 1 for v in values):
                        total.calib1_manual_is_total = False
                    elif all(v == 0 for v in values):
                        total.calib1_manual_is_total = True
                    else:
                        total.calib1_manual_is_total = False

                elif group_id == 2:
                    total.list_false_sensors_calib2 = []
                    total.list_done_sensors_calib2 = []
                    #check value
                    N1 = len(image.sensor_groups[1])
                    for i, val in enumerate(values):
                        global_i = i + N1
                        if val == 1:
                            total.list_false_sensors_calib2.append(global_i)
                        else:
                            total.list_done_sensors_calib2.append(global_i)
                    #check passed/fail
                    if all(v == 1 for v in values):
                        total.calib2_manual_is_total = False
                    elif all(v == 0 for v in values):
                        total.calib2_manual_is_total = True
                    else:
                        total.calib2_manual_is_total = False

            if data_type == "AUTO" and not Flags.onclick_mode:
                if group_id == 1:                
                    total.list_false_sensors_calib1_auto = []
                    total.list_done_sensors_calib1_auto = []
                    #check value
                    for i, val in enumerate(values):
                        if val == 1:
                            total.list_false_sensors_calib1_auto.append(i)
                        else:
                            total.list_done_sensors_calib1_auto.append(i)
                    #check passed/fail
                    if all(v == 1 for v in values):
                        total.calib1_auto_is_total = False
                    elif all(v == 0 for v in values):
                        total.calib1_auto_is_total = True
                    else:
                        total.calib1_auto_is_total = False

                elif group_id == 2:
                    total.list_false_sensors_calib2_auto = []
                    total.list_done_sensors_calib2_auto = []
                    #check value
                    N1 = len(image.sensor_groups[1])
                    for i, val in enumerate(values):
                        global_i = i + N1
                        if val == 1:
                            total.list_false_sensors_calib2_auto.append(global_i)
                        else:
                            total.list_done_sensors_calib2_auto.append(global_i)
                    #check passed/fail
                    if all(v == 1 for v in values):
                        total.calib2_auto_is_total = False
                    elif all(v == 0 for v in values):
                        total.calib2_auto_is_total = True
                    else:
                        total.calib2_auto_is_total = False

    # Btn Normal
    def handle_normal(cmd, label_cl=None, label_check=None):
        if not Flags.is_connected:
            logger.error("Cannot onclick: COM Port is not opened")
            if label_cl:
                label_cl.setStyleSheet("background-color: red")
            if label_check:
                label_check.setStyleSheet("background-color: red")
            return

        if not Flags.onclick_mode:
            logger.error("mode AUTO cannot onclick")
            return

        serial_reader.write_data(cmd)

        if label_cl:
            label_cl.setStyleSheet("background-color: green")
        if label_check:
            label_check.setStyleSheet("background-color: green")

        if cmd == Command.calib_1 or cmd == Command.calib_2 : 
            if not total_timer.isActive() or not index_manual_timer.isActive():
                total_timer.start()
                index_manual_timer.start()

    #Btn Calib 1
    main_window.btnCalib1.clicked.connect(
        lambda: handle_normal(
            Command.calib_1,
            label_cl=main_window.ColorCl1
        )
    )

    #Btn Calib 2
    main_window.btnCalib2.clicked.connect(
        lambda: handle_normal(
            Command.calib_2,
            label_cl=main_window.ColorCl2
        )
    )

    #Btn Check 1
    main_window.btnCheck1.clicked.connect(
        lambda: handle_normal(
            Command.check_1,
            label_check=main_window.ColorCheck1
        )
    )

    #Btn Check 2
    main_window.btnCheck2.clicked.connect(
        lambda: handle_normal(
            Command.check_2,
            label_check=main_window.ColorCheck2
        )
    )

    #Btn Compare
    def handle_compare(cmd, value, label_cl, label_check, compare_flag_name, onclick_name):
        if not Flags.onclick_mode:
            logger.error("mode AUTO cannot onclick")
            return

        if Flags.is_connected:
            if getattr(Flags, compare_flag_name):
                setattr(Flags, onclick_name, True)
                full_cmd = cmd + str(value) + "\n"
                logger.info(full_cmd)
                serial_reader.write_data(full_cmd)
                label_cl.setStyleSheet("background-color: red")
                label_check.setStyleSheet("background-color: red")
            else:
                pass
        else:
            logger.error("Cannot compare: COM Port is not opened")

    # Btn Compare 1
    main_window.btnCompare1.clicked.connect(
        lambda: handle_compare(
            Command.compare_1,
            Command.value_compare_1,
            main_window.ColorCl1,
            main_window.ColorCheck1,
            "is_compare1",
            "onclick_compare_1"
        )
    )

    # Btn Compare 2
    main_window.btnCompare2.clicked.connect(
        lambda: handle_compare(
            Command.compare_2,
            Command.value_compare_2,
            main_window.ColorCl2,
            main_window.ColorCheck2,
            "is_compare2",
            "onclick_compare_2"
        )
    )

    # Btn Mode
    def power_mode():
        if not Flags.is_connected:
            logger.error("Cannot switch mode: COM Port is not opened")
            return

        total.list_false_sensors_calib1 = []
        total.list_done_sensors_calib1 = []
        total.list_false_sensors_calib2 = []
        total.list_done_sensors_calib2 = []
        total.list_false_sensors_calib1_auto = []
        total.list_done_sensors_calib1_auto = []
        total.list_false_sensors_calib2_auto = []
        total.list_done_sensors_calib2_auto = []

        total.calib1_auto_is_total = False
        total.calib2_auto_is_total = False
        total.calib1_manual_is_total = False
        total.calib2_manual_is_total = False

        image.sensor_colors = {}
        image.draw_points()

        Flags.onclick_mode = not Flags.onclick_mode
        if Flags.onclick_mode:
            main_window.btnMode.setText("AUTO")
            logger.info("mode : MANUAL ---> stop index_auto_timer")
            logger.info("mode : MANUAL ---> start index_manual_timer")
            logger.info("mode : MANUAL ---> restart total_timer")
            index_auto_timer.stop()
            index_manual_timer.start()
            total_timer.start()
        else:
            main_window.btnMode.setText("MANUAL")
            logger.info("mode : AUTO ---> start index_auto_timer")
            logger.info("mode : AUTO ---> stop index_manual_timer")
            logger.info("mode : AUTO ---> restart total_timer")
            index_auto_timer.start()
            index_manual_timer.stop()
            total_timer.start()
    main_window.btnMode.clicked.connect(power_mode)

    # Btn Reset
    def power_reset():
        if not Flags.onclick_mode:
            logger.error("mode AUTO cannot onclick RESET")
            return

        if not Flags.is_connected:
            logger.error("Cannot reset: COM Port is not opened")
            return

        total.list_false_sensors_calib1 = []
        total.list_done_sensors_calib1 = []
        total.list_false_sensors_calib2 = []
        total.list_done_sensors_calib2 = []
        total.list_false_sensors_calib1_auto = []
        total.list_done_sensors_calib1_auto = []
        total.list_false_sensors_calib2_auto = []
        total.list_done_sensors_calib2_auto = []
        Flags.onclick_compare_1 = False
        Flags.onclick_compare_2 = False

        total.calib1_auto_is_total = False
        total.calib2_auto_is_total = False
        total.calib1_manual_is_total = False
        total.calib2_manual_is_total = False

        image.sensor_colors = {}
        image.draw_points()

        index_manual_timer.stop()
        index_auto_timer.stop()
        total_timer.stop()

        main_window.Total1.setText("N/A")
        main_window.Total1.setStyleSheet("font-weight: bold; background-color: none;")
        main_window.Total2.setText("N/A")
        main_window.Total2.setStyleSheet("font-weight: bold; background-color: none;")
        main_window.ColorCl1.setStyleSheet("background-color: red")
        main_window.ColorCl2.setStyleSheet("background-color: red")
        main_window.ColorCheck1.setStyleSheet("background-color: red")
        main_window.ColorCheck2.setStyleSheet("background-color: red")

        logger.info("Reset Compare")
        logger.info("mode : RESET ---> stop index_auto_timer")
        logger.info("mode : RESET ---> stop index_manual_timer")
        logger.info("mode : RESET ---> stop total_timer")
    main_window.btnReset.clicked.connect(power_reset)

    #update compare index manual
    def update_compare_index_manual():
        if not Flags.is_connected:
            return
        #manual
        if Flags.onclick_compare_1 and hasattr(total, "list_false_sensors_calib1"):

            for i in total.list_false_sensors_calib1:
                image.set_sensor_color(image.sensor_groups[0][i].id, "red")

            for i in total.list_done_sensors_calib1:
                image.set_sensor_color(image.sensor_groups[0][i].id, "green")

        if Flags.onclick_compare_2 and hasattr(total, "list_false_sensors_calib2"):
            N1 = len(image.sensor_groups[1])

            for i_shifted in total.list_false_sensors_calib2:
                i = i_shifted - N1
                image.set_sensor_color(image.sensor_groups[1][i].id, "red")

            for i_shifted in total.list_done_sensors_calib2:
                i = i_shifted - N1
                image.set_sensor_color(image.sensor_groups[1][i].id, "green")

    #update compare index auto
    def update_compare_index_auto():
        if not Flags.is_connected:
            return

        #calib1
        for i in total.list_false_sensors_calib1_auto:
            image.set_sensor_color(image.sensor_groups[0][i].id, "red")

        for i in total.list_done_sensors_calib1_auto:
            image.set_sensor_color(image.sensor_groups[0][i].id, "green")

        #calib2
        N1 = len(image.sensor_groups[1])
        for i_shifted in total.list_false_sensors_calib2_auto:
            i = i_shifted - N1
            image.set_sensor_color(image.sensor_groups[1][i].id, "red")

        for i_shifted in total.list_done_sensors_calib2_auto:
            i = i_shifted - N1
            image.set_sensor_color(image.sensor_groups[1][i].id, "green")

    #update compare total
    def update_compare_total():
        if not Flags.is_connected:
            return

        #update total
        if total.calib1_manual_is_total or total.calib1_auto_is_total:
            main_window.Total1.setText("PASSED")
            main_window.Total1.setStyleSheet("font-weight: bold; background-color: green;")
        else:    
            main_window.Total1.setText("FAILED")
            main_window.Total1.setStyleSheet("font-weight: bold; background-color: red;")

        if total.calib2_manual_is_total or total.calib2_auto_is_total:
            main_window.Total2.setText("PASSED")
            main_window.Total2.setStyleSheet("font-weight: bold; background-color: green;")
        else :
            main_window.Total2.setText("FAILED")
            main_window.Total2.setStyleSheet("font-weight: bold; background-color: red;")


    #timer update index manual compare
    index_manual_timer = QTimer(main_window)
    index_manual_timer.setInterval(100)
    index_manual_timer.timeout.connect(update_compare_index_manual)
    index_manual_timer.start()

    #timer update index manual compare
    index_auto_timer = QTimer(main_window)
    index_auto_timer.setInterval(100)
    index_auto_timer.timeout.connect(update_compare_index_auto)
    index_auto_timer.start()

    #timer update total compare
    total_timer = QTimer(main_window)
    total_timer.setInterval(100)
    total_timer.timeout.connect(update_compare_total)
    total_timer.start()

    #timer update value compare 
    compare_value_timer(main_window)

    #main window
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    try:
        cfg_path = get_resource_path("Config/config_cube20l.json")
        cfg = load_config(cfg_path)
        logger = Logger(cfg.logfile)
        main(cfg,logger)
    except Exception as e:
        logger.info("Application close:", e)
    
