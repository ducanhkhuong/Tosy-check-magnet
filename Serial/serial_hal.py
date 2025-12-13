from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QIODevice, QByteArray

class SerialReader(QObject):                    # inherits from QObject
    data_received = pyqtSignal(str)             # create signal 'data_received' that emits a string
    is_connect = False
    def __init__(self, port_name, baud_rate=115200, parent=None):
        super().__init__(parent)
        self.serial_port = QSerialPort(port_name)
        self.serial_port.setBaudRate(baud_rate)
        self.serial_port.setDataBits(QSerialPort.Data8)
        self.serial_port.setParity(QSerialPort.NoParity)
        self.serial_port.setStopBits(QSerialPort.OneStop)
        self.serial_port.setFlowControl(QSerialPort.NoFlowControl)

        if not self.serial_port.open(QIODevice.ReadWrite):                      # Open serial port
            print("Error opening serial port:", self.serial_port.errorString())
            return

        self.serial_port.readyRead.connect(self.read_data)                      # connect to read_data Qt slot
        self.is_connect = True

    def write_data(self, data):
        if self.serial_port.isOpen():
            self.serial_port.write(bytearray(data, "utf-8"))
            return True
        else:
            return False

    @pyqtSlot()
    def read_data(self):
        while self.serial_port.canReadLine():
            raw = self.serial_port.readLine()
            line = bytes(raw).decode("utf-8", errors="ignore").strip()

            if line:
                self.data_received.emit(line)


    def close(self):
        if self.serial_port.isOpen():
            self.serial_port.close()