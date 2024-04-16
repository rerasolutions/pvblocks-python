
from pvblocks_io_rera import pvblocks_system

print(pvblocks_system.show_version())

pvblock = pvblocks_system.PvBlocks('COM16')


print(pvblock.init_system())
print(pvblock.scanblocks())

for b in pvblock.Blocks:
    print(b.Guid)
    print(pvblocks_system.PvBlocks.TYPES[b.Type])

for b in pvblock.Blocks:
    print(pvblock.read_data(b))