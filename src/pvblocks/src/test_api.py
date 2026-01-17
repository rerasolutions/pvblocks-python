host = '100.105.180.7'
apikey = 'c88d8c2c-9488-4e5f-82eb-e703feeb543a'

from pvblocks import pvblocks_api

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi(host ,apikey)
pvblocks.Init()


def DeleteAllPvDevices():
    for s in pvblocks.get_pvdevices():
        pvblocks.delete_pvdevice(s['id'])

def DeleteAllSchedules():
    for s in pvblocks.get_schedules():
        pvblocks.delete_schedule(s['id'])

def RecreateSchedules():
    pvblocks.create_schedule(1, False)
    pvblocks.create_schedule(1, True)
    pvblocks.create_schedule(5, True)


def RecreateBlockLabels():
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
            label = "IVMPP-{}".format(channel)
            print(label)
            pvblocks.write_block_label(b['id'], label)
        if b['type'] == "RR-1741":
            location = 4* b['usbNr'] + b['boardNr'] + 1
            label = "IVTEMP-{}".format(location)
            print(label)
            pvblocks.write_block_label(b['id'], label)

def RecreatePvDevices():
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
            label = "PvDevice-{}".format(channel)
            pvblocks.create_pvdevice(label)


# RecreateBlockLabels()
# DeleteAllSchedules()
# RecreateSchedules()
# DeleteAllPvDevices()



