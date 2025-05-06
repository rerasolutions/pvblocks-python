from win32com.client import constants

from pvblocks import pvblocks_system
from pvblocks import constants
from pvblocks import IvMpp
from time import sleep

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM16')


if pvblocks.init_system():
    print("init ok")
else:
    print("failed")

print("scanning blocks available")

if pvblocks.scanblocks():
    print("ok")
else:
    print("failed")

iv_mpp = None

for b in pvblocks.Blocks:
    print(pvblocks_system.PvBlocks.TYPES[b.Type])
    if b.Type == 20:
        iv_mpp = b

ivpoint = pvblocks.execute_method(iv_mpp, constants.Rr1700Function.IvMppReadIVPoint)
print(ivpoint)
sleep(1)
pvblocks.execute_method(iv_mpp, constants.Rr1700Function.IvMppApplyState, [constants.IvMppState.VoltageBias, 0.15])


pvblocks.close_system()