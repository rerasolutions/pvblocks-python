from pvblocks import pvblocks_api
from pvblocks import constants
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
    TemperatureScheduleId = pvblocks.create_schedule(1, False)['id']
    IvPointScheduleId = pvblocks.create_schedule(1, True)['id']
    IvCurveScheduleId = pvblocks.create_schedule(5, True)['id']
    return (TemperatureScheduleId, IvPointScheduleId, IvCurveScheduleId)

def AssignTemperatureToSchedule(scheduleId):
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1741":
            pvblocks.add_command_to_schedule(scheduleId, b['id'], b['commands'][0])

def AssignTIvCurveToSchedule(scheduleId):
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            for c in b['commands']:
                if c['name'] == 'StartIvCurve':
                    pvblocks.add_command_to_schedule(scheduleId, b['id'], c)

def AssignTIvPointToSchedule(scheduleId):
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            for c in b['commands']:
                if c['name'] == 'MeasureIvPoint':
                    pvblocks.add_command_to_schedule(scheduleId, b['id'], c)

def RecreateBlockLabels():
    for b in pvblocks.Blocks:
        if b['type'] == "RR-1727":
            channel = pvblocks_api.get_channel_number(b['usbNr'], b['boardNr'], b['channelNr'])
            label = "IVMPP-{}".format(channel)
            print(label)
            pvblocks.write_block_label(b['id'], label)
            for s in b['sensors']:
                if s['name'] == 'ivcurve':
                    pvblocks.update_sensor_description(s['id'], "ivcurve-{}".format(channel))
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


def SetStateForAllRr1727(state, voltageBias = 0, block_list = None):
    if block_list is None:
        block_list = pvblocks.Blocks

    for b in block_list:
        if b['type'] == "RR-1727":
            pvblocks.write_rr1727_state(b['guid'], state, voltageBias)

def SetSweepParametersForAllRr1727(points, integration_cycles, sweep_type, block_list = None):
    if block_list is None:
        block_list = pvblocks.Blocks

    for b in block_list:
        if b['type'] == "RR-1727":
            pvblocks.write_rr1727_default_sweep(b['id'], points, integration_cycles, sweep_type)

def SetCalibrationValuesForAllRr1727(A, B, C, D, block_list = None):
    if block_list is None:
        block_list = pvblocks.Blocks

    for b in block_list:
        print(b['label'])
        if b['type'] == "RR-1727":
            pvblocks.write_rr1727_calibration_values(b['guid'], A, B, C, D)

def SetMppParametersForAllRr1727(p1, p2, p3, p4, block_list = None):
    if block_list is None:
        block_list = pvblocks.Blocks

    for b in block_list:
        print(b['label'])
        if b['type'] == "RR-1727":
            pvblocks.write_rr1727_mpp_values(b['guid'], p1, p2, p3, p4)

def ShowBlocks(block_list = None):
    if block_list is None:
        block_list = pvblocks.Blocks

    for b in block_list:
        print(b['label'])

# DeleteAllPvDevices()
# RecreateBlockLabels()
# RecreatePvDevicesAndAssign()
# DeleteAllSchedules()
# (TemperatureScheduleId, IvPointScheduleId, IvCurveScheduleId) = RecreateSchedules()
# AssignTemperatureToSchedule(TemperatureScheduleId)
# AssignTIvCurveToSchedule(IvCurveScheduleId)
# AssignTIvPointToSchedule(IvPointScheduleId)
# SetStateForAllRr1727(constants.VOC)
# SetSweepParametersForAllRr1727(150, 5, constants.SWEEP_ISC_TO_VOC)
# SetCalibrationValuesForAllRr1727(0.125, 0, 10, 0)
# SetMppParametersForAllRr1727(0.75, 0, 0.01, 100)
