import time
import pyvisa
from pvblocks import pvblocks_system

import matplotlib.pyplot as plt
import numpy as np



from pvlib.ivtools.utils import rectify_iv_curve
import numpy as np


full_scale = 0.1
shunt = 0.499605

reading_percentage = 0.05
fs_percentage = 0.05
allowed_error =  fs_percentage * full_scale / 100.0

print("Allowed range error: " + str(allowed_error))

currents = [0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080, 0.090, 0.100]
currents = [0.10, 0.090, 0.080, 0.070, 0.060, 0.050, 0.040, 0.030, 0.020, 0.010]


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


#dmm_i.write("VOLT:NPLC 0.2")
#dmm_v.write("VOLT:NPLC 0.2")

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM8')


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



real_voltages = []
real_currents = []
measured_voltages = []
measured_currents = []





psu_set_voltage(4);
psu_set_current(currents[0]);
psu_on()
print("comparing currents")
iv_mpp.ApplyIsc()
time.sleep(2)

for i in currents:
    psu_set_current(i);
    time.sleep(2)
    ivpoint = iv_mpp.read_ivpoint()
    current = ivpoint.current
    current_real = float(dmm_i.query("MEAS?")) / shunt
    real_currents.append(current_real)
    measured_currents.append(current)

    diff = abs(current-current_real)
    allowed_error = (fs_percentage * full_scale / 100.0) + (reading_percentage * current_real/100.0)
    true_error = diff
    s = "PASS"
    if( true_error > allowed_error ):
        s = "FAIL"
    print("%s %f:%f:%f:%f" % (s, current_real, current, current-current_real, 100.0*((current-current_real)/current_real)))

pvblocks.close_system()
psu_off()

