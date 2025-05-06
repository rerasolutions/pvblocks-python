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
        40: 'PV-TEMP 4x Pt100 readout block',
        50: 'PV-MOD digital modbus module'
    }

    def __init__(self, serialport):
        # type: (UART_Adapter) -> None
        self.uart = serial.Serial(serialport,
                                  baudrate=115200,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE,
                                  timeout=1)

    def init_system(self):
        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.Alive]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        if len(bts) != 2:
            raise exceptions.NoResponseException()
        return bts[0] == 3 and bts[1] == constants.Rr1700Command.Alive


    def close_system(self):
        self.uart.close()


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

    def reset_controller(self):
        if not self.uart.is_open:
            self.uart.open()

        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.ResetController]))
        sleep(3)


    def open_block(self, pvblock):
        self.uart.write(serial.to_bytes([1,
                                         constants.Rr1700Command.OpenModule,
                                         0,
                                         pvblock.bytes[0],
                                         pvblock.bytes[1],
                                         pvblock.bytes[2],
                                         pvblock.bytes[3],
                                         pvblock.bytes[4],
                                         pvblock.bytes[5],
                                         pvblock.bytes[6],
                                         pvblock.bytes[7]]))
        sleep(0.5)
        bts = ReadSerial(self.uart)

        return len(bts) == 3

    def close_block(self, pvblock):
        self.uart.write(serial.to_bytes([1,
                                         constants.Rr1700Command.CloseModule,
                                         pvblock.bytes[0],
                                         pvblock.bytes[1],
                                         pvblock.bytes[2],
                                         pvblock.bytes[3],
                                         pvblock.bytes[4],
                                         pvblock.bytes[5],
                                         pvblock.bytes[6],
                                         pvblock.bytes[7]]))
        sleep(0.5)
        bts = ReadSerial(self.uart)

        return len(bts) == 3

    def read_statusbyte(self, pvblock):
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.GetStatus]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        if len(bts) < 10:
            raise exceptions.UnexpectedResponseException()
        return StatusByte(bts)


    def read_data(self, pvblock):
        try:
            if pvblock.Type == 20:
                return self.read_ivpoint(pvblock)
            if pvblock.Type == 30:
                return self.read_irradiances(pvblock)
        except:
            print("Exception raised")
        finally:
            self.close_block(pvblock)

        raise exceptions.NoReadDataImplementedException()

    def read_irradiances(self, pvblock):
        if self.open_block(pvblock):
            self.uart.write(serial.to_bytes([2, constants.Rr1700Command.ReadCommand]))
            sleep(0.5)
            bts = ReadSerial(self.uart)
            if len(bts) < 10:
                raise exceptions.UnexpectedResponseException()

            r1 = int.from_bytes(bts[3:7], "little") / 1000.0
            r2 = int.from_bytes(bts[7:11], "little") / 1000.0
            if bts[2] == 16:
                r3 = int.from_bytes(bts[11:15], "little") / 1000.0
                r4 = int.from_bytes(bts[15:19], "little") / 1000.0
                return r1, r2, r3, r4
            else:
                return r1, r2


        else:
            raise exceptions.CannotOpenBlockException()

        return (0, 0, 0, 0)

    def read_ivpoint(self, pvblock):
        return (0, 0)

    def execute_method(self, pvblock, method, parameters=None):

        ivpoint = None

        if pvblock is None:
            raise exceptions.PvBlocksIsNoneException()

        status = None
        if parameters is None:
            parameters = []
        if method not in pvblock.SupportedMethods:
            raise exceptions.MethodNotSupportedException()

        self.open_block(pvblock)

        if method == constants.Rr1700Function.IvMppReadIVPoint:
            status = self.read_statusbyte(pvblock)
            self.uart.write(serial.to_bytes([2, constants.Rr1700Command.ReadCommand]))
            sleep(0.5)
            bts = ReadSerial(self.uart)
            if len(bts) < 15:
                raise exceptions.UnexpectedResponseException()

            if bts[2] != 12:
                raise exceptions.UnexpectedResponseException()

            r1 = int.from_bytes(bts[3:7], "little") / 1000.0
            r2 = int.from_bytes(bts[7:11], "little") / 1000.0
            ivpoint = IvPoint(r1, r2)

        self.close_block(pvblock)
        return ivpoint


class PvBlock(object):
    def __init__(self, bytes):
        self.bytes = bytes[0:8]
        id = int.from_bytes(bytearray(self.bytes), 'little')
        self.Guid = uuid.UUID(int=id)
        self.Type = bytes[8]
        self.SupportedMethods = self.get_supported_methods()


    def get_supported_methods(self):
        supported_methods = []
        if self.Type == 20:
            supported_methods.append(constants.Rr1700Function.IvMppReadIVPoint)
            supported_methods.append(constants.Rr1700Function.IvMppSetMode)

        return supported_methods

class StatusByte(object):
    def __init__(self, bytes):
        self.blocktype = bytes[2]
        self.token = bytes[3]
        self.mode = bytes[4]
        self.statusbytes = bytes[5:]


class IvPoint(object):
    def __init__(self, voltage, current):
        self.voltage = voltage
        self.current = current
        self.power = voltage * current
