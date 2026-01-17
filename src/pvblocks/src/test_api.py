

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
            for s in b['sensors']:
                if s['name'] == 'ivcurve':
                    pvblocks.update_sensor_description(s['id'], "curve-{}".format(channel))
                else:
                    pvblocks.update_sensor_description(s['id'], "ivpoint-{}".format(channel))

        if b['type'] == "RR-1741":
            location = 4* b['usbNr'] + b['boardNr'] + 1
            label = "IVTEMP-{}".format(location)
            print(label)
            pvblocks.write_block_label(b['id'], label)
            cnt = 1
            for s in b['sensors']:
                pvblocks.update_sensor_description(s['id'], "TC-{}".format(cnt))
                cnt = cnt + 1


def RecreatePvDevices():
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
            label = "PvDevice-{}".format(channel)
            pvblocks.create_pvdevice(label)

def RecreatePvDevicesAndAssign():
    board_tc_sensor_ids = {}
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1741":
            board_tc_sensor_ids['boardNr{}'.format(b['boardNr'])] = [b['sensors'][0]['id'], b['sensors'][1]['id']]

    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
            label = "PvDevice-{}".format(channel)
            dev = pvblocks.create_pvdevice(label)
            pvblocks.attach_sensor_to_pvdevice(b['sensors'][0]['id'] ,dev['id'])
            pvblocks.attach_sensor_to_pvdevice(b['sensors'][1]['id'], dev['id'])
            tc1_id = board_tc_sensor_ids['boardNr{}'.format(b['boardNr'])][0]
            tc2_id = board_tc_sensor_ids['boardNr{}'.format(b['boardNr'])][1]
            if b['channelNr'] < 4:
                pvblocks.attach_sensor_to_pvdevice(tc1_id, dev['id'])
            else:
                pvblocks.attach_sensor_to_pvdevice(tc2_id, dev['id'])

DeleteAllPvDevices()
RecreateBlockLabels()
RecreatePvDevicesAndAssign()
DeleteAllSchedules()
RecreateSchedules()





