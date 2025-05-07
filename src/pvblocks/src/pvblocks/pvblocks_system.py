from . import VERSION
from . import exceptions
from . import constants
import serial
import uuid
import struct
from time import sleep
from enum import IntEnum



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
        self.Blocks = []
        self.IvMppBlocks = []
        self.PvIrrBlocks = []

    def init_system(self):
        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.Alive]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        if len(bts) != 2:
            raise exceptions.NoResponseException()
        return bts[0] == 3 and bts[1] == constants.Rr1700Command.Alive


    def close_system(self):
        self.uart.close()


    def scan_blocks(self):
        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.ListModules]))
        sleep(2)
        bts = ReadSerial(self.uart)

        if (bts[0] != 3) or (bts[1] != constants.Rr1700Command.ListModules):
            raise exceptions.UnexpectedResponseException()

        module_count = bts[3]
        self.Blocks = []
        self.IvMppBlocks = []
        self.PvIrrBlocks = []
        for index in range(module_count):
            match bts[(index * 9) + 4 + 8]:
                case 20:
                    blck = IvMpp(bts[(index * 9) + 4: (index * 9) + 13], self.uart)
                    self.IvMppBlocks.append(blck)
                case 30:
                    blck = PvIrr(bts[(index * 9) + 4: (index * 9) + 13], self.uart)
                    self.PvIrrBlocks.append(blck)
                case _:
                    blck = PvBlock(bts[(index * 9) + 4: (index * 9) + 13], self.uart)
                    self.Blocks.append(blck)


        return module_count > 0

    def reset_controller(self):
        if not self.uart.is_open:
            self.uart.open()

        self.uart.write(serial.to_bytes([1, constants.Rr1700Command.ResetController]))
        sleep(3)


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





class PvBlock(object):
    def __init__(self, bytes, uart):
        self.bytes = bytes[0:8]
        id = int.from_bytes(bytearray(self.bytes), 'little')
        self.Guid = uuid.UUID(int=id)
        self.Type = bytes[8]
        self.uart = uart

    def open(self):
        self.uart.write(serial.to_bytes([1,
                                         constants.Rr1700Command.OpenModule,
                                         0,
                                         self.bytes[0],
                                         self.bytes[1],
                                         self.bytes[2],
                                         self.bytes[3],
                                         self.bytes[4],
                                         self.bytes[5],
                                         self.bytes[6],
                                         self.bytes[7]]))
        sleep(0.5)
        bts = ReadSerial(self.uart)

        return len(bts) == 3

    def close(self):
        self.uart.write(serial.to_bytes([1,
                                         constants.Rr1700Command.CloseModule,
                                         self.bytes[0],
                                         self.bytes[1],
                                         self.bytes[2],
                                         self.bytes[3],
                                         self.bytes[4],
                                         self.bytes[5],
                                         self.bytes[6],
                                         self.bytes[7]]))
        sleep(0.5)
        bts = ReadSerial(self.uart)

        return len(bts) == 3


    def read_statusbyte(self):
        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.GetStatus]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        self.close()
        if len(bts) < 10:
            raise exceptions.UnexpectedResponseException()
        return StatusByte(bts)

    def get_info(self):
        status = self.read_statusbyte()
        d = {'firmware': status.firmware, 'hardware': status.hardware}
        return d


class IvMpp(PvBlock):
    def read_ivpoint(self):

        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.ReadCommand]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        self.close()
        if len(bts) < 15:
            raise exceptions.UnexpectedResponseException()

        if bts[2] != 12:
            raise exceptions.UnexpectedResponseException()

        r1 = int.from_bytes(bts[3:7], "little") / 10000.0
        r2 = int.from_bytes(bts[7:11], "little") / 100000.0
        ivpoint = IvPoint(r1, r2)

        return ivpoint

    def ApplyVoc(self):
        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.IdleCommand]))
        sleep(0.5)
        self.close()


    def ApplyMpp(self):
        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.MppCommand]))
        sleep(0.5)
        self.close()

    def ApplyIsc(self):
        voltage = 0.0;
        self.open()
        bytes = list(((int)(1000 * voltage)).to_bytes(4, "little"))
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.VoltageCommand, bytes[0], bytes[1], bytes[2], bytes[3]]))
        sleep(0.5)
        self.close()

    def ApplyVoltageBias(self, voltage):
        self.open()
        bytes = list(((int)(1000 * voltage)).to_bytes(4, "little"))
        self.uart.write(
            serial.to_bytes([2, constants.Rr1700Command.VoltageCommand, bytes[0], bytes[1], bytes[2], bytes[3]]))
        sleep(0.5)
        self.close()

    def measure_ivcurve(self, points, delay_ms, sweepstyle):
        self.open()

        self.uart.write(
            serial.to_bytes([2, constants.Rr1700Command.SetTriggerCommand, 0]))

        sleep(0.5)

        self.uart.write(
            serial.to_bytes([2, constants.Rr1700Command.CurveCommand, points, delay_ms, 0, 0, 0, 0, sweepstyle]))

        while self.uart.inWaiting() != 3:
            sleep(0.01)

        bts = ReadSerial(self.uart)

        status = self.read_statusbyte()
        while status.mode == 5:
            sleep(0.5)
            status = self.read_statusbyte()

        self.close()

        points_measured = status.statusbytes[0]
        curve = self.transfer_curve(points_measured)

        return curve

    def transfer_curve(self, points):
        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.TransferCurveCommand]))
        sleep(0.5)
        availablebytes = 8 + (points * 8) + 1
        toread = self.uart.inWaiting()
        while toread != availablebytes:
            toread = self.uart.inWaiting()
            print(toread)
            sleep(0.1)
        bts = ReadSerial(self.uart)
        self.close()

        voltages = []
        currents = []


        for i in range(int((availablebytes - 1)/8)):
            index = (i * 8) + 1
            voltages.append(int.from_bytes(bts[index:(index+4)], "little") / 10000.0)
            index = index + 4
            currents.append(int.from_bytes(bts[index:(index+4)], "little") / 100000.0)

        return {'voltages': voltages, 'currents': currents}

    def read_calibration(self):
        c = {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0}
        bts = self.read_eeprom(4, 16)
        c['A'] = struct.unpack('<f', bytearray(bts[0:4]))
        c['B'] = struct.unpack('<f', bytearray(bts[4:8]))
        c['C'] = struct.unpack('<f', bytearray(bts[8:12]))
        c['D'] = struct.unpack('<f', bytearray(bts[12:16]))

        return c

    def read_eeprom(self, address, length):
        bts = list(address.to_bytes(2, 'little'))
        self.open()
        self.uart.write(
            serial.to_bytes([2, constants.Rr1700Command.ReadEepromCommand, length, bts[0], bts[1]]))

        while self.uart.inWaiting() != length + 3:
            sleep(0.01)

        bts = ReadSerial(self.uart)
        self.close()
        return bts[3:]


class PvIrr(PvBlock):

    def ReadIrradiances(self):
        self.open()
        self.uart.write(serial.to_bytes([2, constants.Rr1700Command.ReadCommand]))
        sleep(0.5)
        bts = ReadSerial(self.uart)
        if len(bts) < 10:
            raise exceptions.UnexpectedResponseException()

        irradiances = []

        r1 = int.from_bytes(bts[3:7], "little") / 1000.0
        r2 = int.from_bytes(bts[7:11], "little") / 1000.0
        irradiances.append(r1)
        irradiances.append(r2)
        if bts[2] == 16:
            r3 = int.from_bytes(bts[11:15], "little") / 1000.0
            r4 = int.from_bytes(bts[15:19], "little") / 1000.0
            irradiances.append(r3)
            irradiances.append(r4)

        self.close()
        return irradiances

class StatusByte(object):
    def __init__(self, bytes):
        self.blocktype = bytes[2]
        self.token = bytes[3]
        self.mode = bytes[4]
        self.statusbytes = bytes[5:]
        self.firmware = bytes[9]
        self.hardware = bytes[8]


class IvPoint(object):
    def __init__(self, voltage, current):
        self.voltage = voltage
        self.current = current
        self.power = voltage * current

    def __str__(self):
        return "(%f, %f)" % (self.voltage, self.current)


class SweepStyle(IntEnum):
    ISC_TO_VOC = 0,
    SWEEP_VOC_TO_ISC = 1,
    EXTENT_CURVE_DELAY = 2,
    SWEEP_VOC_ISC_VOC = 4,
    SWEEP_ISC_VOC_ISC = 8