from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QIODevice, QTimer
import time

class SerialReader(QObject):

    data_received = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, port_name=None, baud_rate=115200, parent=None):
        super().__init__(parent)

        self.port_name = port_name
        self.baud_rate = baud_rate  
        self.last_rx_time = time.monotonic()

        self.serial = QSerialPort()
        self.serial.setBaudRate(self.baud_rate)
        self.serial.setDataBits(QSerialPort.Data8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(QSerialPort.OneStop)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)

        self.serial.readyRead.connect(self.read_data)
        self.serial.errorOccurred.connect(self.handle_error)

        self.buffer = ""

        self.is_connected = False

        # reconnect timer
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(2000)
        self.reconnect_timer.timeout.connect(self.try_reconnect)

        # watchdog timer
        self.watchdog = QTimer()
        self.watchdog.setInterval(1000)
        self.watchdog.timeout.connect(self.check_connection)


    def connect_port(self):
        if self.port_name is None:
            ports = QSerialPortInfo.availablePorts()
            if not ports:
                self.reconnect_timer.start()
                return

            self.port_name = ports[0].portName()

        self.serial.setPortName(self.port_name)

        if self.serial.isOpen():
            self.serial.close()

        if not self.serial.open(QIODevice.ReadWrite):
            self.is_connected = False
            self.reconnect_timer.start()
            return


        self.serial.clear()
        self.buffer = ""
        self.last_rx_time = time.monotonic() 
        self.is_connected = True
        self.reconnect_timer.stop()

        self.watchdog.start()

        self.connected.emit()

    def try_reconnect(self):

        if self.is_connected:
            return

        ports = QSerialPortInfo.availablePorts()

        for port in ports:

            self.port_name = port.portName()

            self.connect_port()

            if self.is_connected:
                break


    def write(self, data):

        if not self.serial.isOpen():
            return False

        if isinstance(data, str):
            data = data.encode()

        self.serial.write(data)
        self.last_rx_time = time.monotonic()
        return True


    @pyqtSlot()
    def read_data(self):

        while self.serial.canReadLine():

            raw = self.serial.readLine()

            line = bytes(raw).decode("utf-8", errors="ignore").strip()

            if line:
                self.last_rx_time = time.monotonic()
                self.data_received.emit(line)

    def handle_error(self, error):

        if error == QSerialPort.NoError:
            return

        if not self.is_connected:
            return

        if error in (
            QSerialPort.ResourceError,
            QSerialPort.DeviceNotFoundError,
            QSerialPort.PermissionError,
        ):
            QTimer.singleShot(0, self.disconnect_port)

    def disconnect_port(self):

        if not self.is_connected:
            return

        self.is_connected = False

        if self.serial.isOpen():
            self.buffer = ""
            self.serial.clear()
            self.serial.close()

        self.watchdog.stop()

        self.reconnect_timer.start()

        self.disconnected.emit()

    def check_connection(self):

        if not self.serial.isOpen():
            self.disconnect_port()
            return

        now = time.monotonic()

        if now - self.last_rx_time > 8:#8s
            self.disconnect_port()


    def close(self):

        self.reconnect_timer.stop()
        self.watchdog.stop()

        self.is_connected = False 

        if self.serial.isOpen():
            self.serial.close()

#amv