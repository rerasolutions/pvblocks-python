
from pvblocks_io_rera import pvblocks_system

print(pvblocks_system.show_version())

pvblock = pvblocks_system.PvBlocks('COM1')

pvblock.init_system()
