import sys

from pvblocks import pvblocks_api
from src.pvblocks.src.pvblocks.pvblocks_api import get_channel_number

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi('100.105.180.7', '4a8bd150-fa41-4fef-a079-f1a0736d6bba')
pvblocks.Init()

for b in pvblocks.Blocks:
    print(b['label'])
    if b['type'] == "RR-1727":
        channel = get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
        label = "IVMPP-{}".format(channel)
        pvblocks.write_block_label(b['id'], label)