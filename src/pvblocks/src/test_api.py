import sys

from pvblocks import pvblocks_api

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi('100.105.180.7', '4a8bd150-fa41-4fef-a079-f1a0736d6bba')
pvblocks.Init()