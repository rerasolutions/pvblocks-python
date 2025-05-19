from pvblocks import pvblocks_system
from time import sleep
from pvlib.ivtools.utils import rectify_iv_curve
import numpy as np

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM16')
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

#print(iv_mpp.get_info())
ivpoint = iv_mpp.read_ivpoint()
print(ivpoint)
curve = iv_mpp.measure_ivcurve(100, 20, 0)
(v, i) = rectify_iv_curve(curve['voltages'], curve['currents'])
p = v * i
voc = v[-1]
isc = i[0]
index_max = np.argmax(p)
impp = i[index_max]
vmpp = v[index_max]
pmax = p[index_max]
ff = pmax/(voc * isc)
pmax = p[index_max]


pvblocks.close_system()