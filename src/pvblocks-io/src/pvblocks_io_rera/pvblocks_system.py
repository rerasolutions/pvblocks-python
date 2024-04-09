from . import VERSION
import serial

def show_version():
    return VERSION


class PvBlocks(object):
    TYPES = {
        20: 'IV/MPP IV-Curve control and measure PvBlock',
        30: 'PV-IRR 4x analog voltage readout block',
        40: 'PV-TEMP 4x Pt100 readout block'
    }

    def __init__(self, serialport):
        # type: (UART_Adapter) -> None
        self.uart = serial.Serial(serialport,baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE )


    def init_system(self):
        self.uart.open()
        self.uart.write(bytearray([1, 100]))
        bts = self.uart.read(2)
        self.uart.close()
        return bts[0] == 3 & bts[1] == 100

    def scanblocks(self):
        return 10