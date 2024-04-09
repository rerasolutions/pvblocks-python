from . import VERSION
from . import exceptions
from . import constants
import serial
import uuid
from time import sleep


def show_version():
    return VERSION


def ReadSerial(ser):
    out = []
    while ser.inWaiting() > 0:
        out.append(ser.read(1)[0])
    return out


class PvBlocks(object):
    TYPES = {
        20: 'IV/MPP IV-Curve control and measure PvBlock',
        30: 'PV-IRR 4x analog voltage readout block',
        40: 'PV-TEMP 4x Pt100 readout block'
    }

    def __init__(self, serialport):
        # type: (UART_Adapter) -> None
        self.uart = serial.Serial(serialport,
                                  baudrate=115200,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE,
                                  timeout=1 )


    def init_system(self):
        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.Alive]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        if len(bts) != 2:
            raise exceptions.NoResponseException()
        return bts[0] == 3 and bts[1] == constants.Rr1700Command.Alive

    def scanblocks(self):
        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.ListModules]))
        sleep(2)
        bts = ReadSerial(self.uart)

        if (bts[0] != 3) or (bts[1] != constants.Rr1700Command.ListModules):
            raise exceptions.UnexpectedResponseException()

        module_count = bts[3]
        self.Blocks = []
        for index in range(module_count):
            blck = PvBlock(bts[(index * 9) + 4: (index * 9) + 13])
            self.Blocks.append(blck)

        return module_count > 0



class PvBlock(object):
    def __init__(self, bytes):
        a = bytes[0:8]
        id = int.from_bytes(bytearray(a), 'little')
        self.Guid = uuid.UUID(int = id)
        self.Type = bytes[8]