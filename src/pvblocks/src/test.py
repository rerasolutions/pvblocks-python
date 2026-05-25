from pvblocks import pvblocks_system
from pvlib.ivtools.utils import rectify_iv_curve
import numpy as np
import time
import sys

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM5')


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
start_time = time.time()
for b in pvblocks.IvMppBlocks:
    ivpoint = b.read_ivpoint(leave_open=True)
    print(ivpoint)
pvblocks.close_system()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed Time: {elapsed_time} seconds")



#print('measure iv curve 200 points, 20ms')
#start_time = time.time()
#curve = iv_mpp.measure_ivcurve(200, 20, 0)
#end_time = time.time()
#elapsed_time = end_time - start_time
#print(f"Elapsed Time: {elapsed_time} seconds")
#(v, i) = rectify_iv_curve(curve['voltages'], curve['currents'])
#p = v * i
#voc = v[-1]
#isc = i[0]
#index_max = np.argmax(p)
#impp = i[index_max]
#vmpp = v[index_max]
#pmax = p[index_max]
#ff = pmax/(voc * isc)
#pmax = p[index_max]


pvblocks.close_system()