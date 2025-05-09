from pvblocks import pvblocks_system
from time import sleep

print("PV-Blocks version: " + pvblocks_system.show_version())

pvblocks = pvblocks_system.PvBlocks('COM16')


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
#curve = iv_mpp.MeasureIvCurve(100, 20, 0)

#pvblocks.close_system()