host = '100.105.180.7'
apikey = '4a8bd150-fa41-4fef-a079-f1a0736d6bba'

from pvblocks import pvblocks_api

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi(host ,apikey)
pvblocks.Init()

for b in pvblocks.Blocks:
    print(b['label'])
    if b['type'] == "RR-1727":
        channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
        label = "IVMPP-{}".format(channel)
        pvblocks.write_block_label(b['id'], label)
    if b['type'] == "RR-1741":
        location = 4* b['usbNr'] + b['boardNr'] + 1
        label = "IVTEMP-{}".format(location)
        pvblocks.write_block_label(b['id'], label)