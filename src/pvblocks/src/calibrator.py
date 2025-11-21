import time
import pyvisa
from pvblocks import pvblocks_system

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from pvlib.ivtools.utils import rectify_iv_curve
import numpy as np


calibrate_voltage = True
calibrate_current = False

shunt = 0.499605
voltages = [2, 4, 6, 8, 10, 12, 14, 16, 18]
currents = [0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080, 0.090, 0.100]

A = []
B = []
C = []
D = []
a_v = -1
b_v = -1
a_i = -1
b_i = -1
rm = pyvisa.ResourceManager()

print(rm.list_resources())
psu = rm.open_resource("ASRL12::INSTR")
dmm_i = rm.open_resource("USB0::0x0957::0x0607::MY47011784::INSTR")
dmm_v = rm.open_resource("USB0::0x0957::0x0A07::MY48003521::INSTR")

def psu_set_voltage(voltage):
    psu.write("VSET1:%f" % (voltage))
    time.sleep(1)

def psu_set_current(current):
    psu.write("ISET1:%f" % (current))
    time.sleep(1)

def psu_on():
    psu.write("OUT1")
    time.sleep(1)

def psu_off():
    psu.write("OUT0")

dmm_v.clear()
dmm_i.clear()
dmm_v.timeout = 60000
print(dmm_v.query("*IDN?"))
print(dmm_i.query("*IDN?"))
print(psu.query("*IDN?"))

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM8')
import matplotlib.pyplot as plt

if pvblocks.init_system():
    print("init ok")
else:
    print("failed")

print("scanning available blocks")

if pvblocks.scan_blocks():
    print("ok")
else:
    print("failed")



iv_mpp = None

for b in pvblocks.Blocks:
    print(pvblocks_system.PvBlocks.TYPES[b.Type])

for b in pvblocks.IvMppBlocks:
    print(pvblocks_system.PvBlocks.TYPES[b.Type])

for b in pvblocks.PvIrrBlocks:
        print(pvblocks_system.PvBlocks.TYPES[b.Type])

if len(pvblocks.IvMppBlocks) > 0:
    iv_mpp = pvblocks.IvMppBlocks[0]



print(iv_mpp.get_info())

for loop in range(1):

    real_voltages = []
    real_currents = []
    measured_voltages = []
    measured_currents = []


    if calibrate_voltage:
        print("calibrating voltages")
        iv_mpp.write_voltage_calibration(16,0)
        iv_mpp.ApplyVoc()
        psu_set_voltage(voltages[0]);
        psu_on();
        time.sleep(2)

        for v in voltages:
            psu_set_voltage(v);
            ivpoint = iv_mpp.read_ivpoint()
            voltage = ivpoint.voltage * 16.0
            voltage_real = float(dmm_v.query("MEAS?"))
            real_voltages.append(voltage_real)
            measured_voltages.append(voltage)
            print("real:measured: %f : %f" % (voltage_real, voltage))

        a_v, b_v = np.polyfit(real_voltages, measured_voltages, 1)
        A.append(a_v)
        B.append(b_v)
        fit_values = []
        for v in real_voltages:
            fit_values.append(v * a_v + b_v)

        plt.plot(real_voltages, measured_voltages, marker='o', linestyle='None')
        plt.plot(real_voltages, fit_values)
        plt.show()

    if calibrate_current:
        psu_set_voltage(voltages[1]);
        psu_set_current(currents[0]);
        print("calibrating currents")
        iv_mpp.write_current_calibration(4, 0)
        iv_mpp.ApplyIsc()
        time.sleep(2)

        for i in currents:
            psu_set_current(i);
            ivpoint = iv_mpp.read_ivpoint()
            current = ivpoint.current * 4.0
            current_real = float(dmm_i.query("MEAS?")) / shunt
            real_currents.append(current_real)
            measured_currents.append(current)
            print("real:measured: %f : %f" % (current_real, current))


        a_i,b_i = np.polyfit(real_currents, measured_currents, 1)
        C.append(a_i)
        D.append(b_i)

        fit_values = []
        for i in real_currents:
            fit_values.append(i * a_i + b_i)

        plt.plot(real_currents, measured_currents, marker='o', linestyle='None')
        plt.plot(real_currents, fit_values)
        plt.show()


    print("(A, B, C, D): (%f, %f, %f, %f)" % (a_v, b_v, a_i, b_i))


psu_off()

A_result = np.average(A)
B_result = np.average(B)
C_result = np.average(C)
D_result = np.average(D)

print("IV/MPP calibration values (A, B, C, D): (%f, %f, %f, %f)" % (A_result, B_result, C_result, D_result))

if calibrate_voltage:
    iv_mpp.write_voltage_calibration(A_result,B_result)

if calibrate_current:
    iv_mpp.write_current_calibration(C_result, D_result)



pvblocks.close_system()