from . import VERSION
from . import exceptions
from . import constants

import requests

EndOfLine = '\r\n'

def show_version():
    return VERSION

def get_channel_number(usbNr, boardNr, channelNr):
    return channelNr + 1  +  (boardNr*8) + usbNr*32

def extract_hex_values(guid_string):
    xx = guid_string[6:8]
    yy = guid_string[21:23]
    return int(xx, 16), int(yy, 16)


# (usb nr, board nr, channel nr), with slotnr = None for a temperature sensor
def GetPosition(guid_string):
    (BlockNr, UsbNr) = extract_hex_values(guid_string)

    if BlockNr > 100:
        return (UsbNr, int((BlockNr -101)/8), (BlockNr -101)%8)

    return (UsbNr, BlockNr-64, None)

def create_rr1741_sensors(input_array):
    result = []
    for md in input_array:
        sens = md['sensors'][0]
        result.append({'id': sens['id'], 'name': sens['name'], 'description': sens['description']})
    return result

def create_rr1720_sensors(input_array):
    result = []
    for sens in input_array:
        result.append({'id': sens['id'], 'name': sens['name'], 'description': sens['description']})
    return result

def create_rr1727_sensors(input_array):
    result = []
    for sens in input_array:
        result.append({'id': sens['id'], 'name': sens['name'], 'description': sens['description']})
    return result


class PvBlocksApi(object):
    TYPES = {
        20: 'IV/MPP IV-Curve control and measure PvBlock',
        27: 'IV/MPP IV-Curve control and measure PvBlock',
        30: 'PV-IRR 4x analog voltage readout block',
        40: 'PV-TEMP 4x Pt100 readout block',
        41: 'PV-TEMP 2x Thermocouple T readout block',
        50: 'PV-MOD digital modbus module'
    }

    def __init__(self, host, api_key):
        self.PVBlocksUrl = 'http://' + host
        self.APIkey = api_key
        self.Blocks = []
        self.PvBaseSystemType = constants.RR1700
        self.token = ''


    def _url(self, path):
        return self.PVBlocksUrl + '/v1' + path

    def get_token(self):
        resp = requests.post(self._url('/authentication/Login'), json={'key': self.APIkey})
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('POST /authentication/Login {}'.format(resp.status_code))
        else:
            return resp.json()['bearer']

    def get(self, endpoint, expected_response_code=200, json_response=True):
        resp = requests.get(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != expected_response_code:
            self.token = self.get_token()
            resp = requests.get(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != expected_response_code:
            raise Exception('GET /' + endpoint + '{}'.format(resp.status_code))
        else:
            if json_response:
                return resp.json()
            else:
                pass
    def post(self, endpoint, payload, expected_response_code=201, json_response=True):
        resp = requests.post(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token}, json=payload)
        if resp.status_code != expected_response_code:
            self.token = self.get_token()
            resp = requests.post(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token}, json=payload)
        if resp.status_code != expected_response_code:
            raise Exception('POST /' + endpoint + '{}'.format(resp.status_code))
        else:
            if json_response:
                return resp.json()
            else:
                pass

    def put(self, endpoint, payload, expected_response_code=204):
        resp = requests.put(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token}, json=payload)
        if resp.status_code != expected_response_code:
            self.token = self.get_token()
            resp = requests.put(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token}, json=payload)
        if resp.status_code != expected_response_code:
            raise Exception('PUT /' + endpoint + '{}'.format(resp.status_code))


    def delete(self, endpoint, expected_response_code=204):
        resp = requests.delete(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != expected_response_code:
            self.token = self.get_token()
            resp = requests.delete(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != expected_response_code:
            raise Exception('DEL /' + endpoint + '{}'.format(resp.status_code))


    def get_activationkey(self, user, pwd):
        try:
            b = self.post('/authentication/Login', {"username": user, "password": pwd},
                              expected_response_code=200)
        except:
            return (False, 'Wrong username password')

        endpoint = '/authentication/ApiKey/activeKey'
        try:
            resp = requests.get(self._url(endpoint), headers={'Authorization': 'Bearer ' + b['bearer']})

            if resp.status_code != 200:
                return (False, 'Wrong username password')
            else:
                return (True, resp.json())
        except:
            return (False, 'Wrong username password')


    def get_api_version(self):
        resp = requests.get(self._url('/info'))
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET /info {}'.format(resp.status_code))
        else:
            return resp.json()['version']

    def Online(self):
        return self.get_api_version() == 'v1'

    def Init(self):
        if self.Online():
            count = self.scan_blocks()
            print('Scanned {} blocks'.format(count))
            print('Found {} blocks to be online'.format(len(self.Blocks)))
        else:
            print('System not online')

    def get_pvdevices(self):
        endpoint = '/PvDevice'
        return self.get(endpoint)

    def create_pvdevice(self, label):
        endpoint = '/PvDevice'
        payload = {
            "Name": label,
            "Serial": "",
            "Manufacturer": "",
            "ManufacturerCode": "",
            "Material": "",
            "IsBiFacial": False,
            "Voc": 0,
            "Isc": 0,
            "Power": 0,
            "Alpha": 0,
            "Beta": 0,
            "TemperatureCoefficient": 0,
            "Area": 0,
            "CellCount": 0,
            "StringCount": 0,
            "TemperatureId": 0,
            "IrradianceId": 0
        }
        return self.post(endpoint, payload)

    def delete_pvdevice(self, id):
        endpoint = '/PvDevice/{}'.format(id)
        self.delete(endpoint)

    def get_pvblocks(self):
        endpoint = '/Block'
        return self.get(endpoint)

    def list_all_unique_identifiers(self):
        blocks = self.get_pvblocks()
        result = []
        for b in blocks:
            result.append((b['uniqueIdentifier']))
        return result

    def scan_blocks(self):
        blks = self.get_pvblocks()
        module_count = len(blks)
        self.Blocks = []
        for b in blks:
            if not(b['online']):
                continue
            (usb, board, channel) = GetPosition(b['uniqueIdentifier'])
            if b['type'] == 'RR-1720':
                sensors = create_rr1720_sensors(b['measurementDevices'][0]['sensors'])
            if b['type'] == 'RR-1727':
                sensors = create_rr1727_sensors(b['measurementDevices'][0]['sensors'])
            if b['type'] == 'RR-1741':
                sensors = create_rr1741_sensors(b['measurementDevices'])

            self.Blocks.append({ "label": b["label"], "id": b["id"],"guid": b['uniqueIdentifier'],
                                "usbNr": usb, "boardNr": board, "channelNr": channel,
                                             "type": b['type'], "sensors": sensors, 'commands': b['availableCommands']})
        return module_count

    def reset_block(self, guid):
        endpoint = '/Hardware/%s/reset' % (guid)
        return self.get(endpoint, expected_response_code=204, json_response=False)

    def write_block_label(self, id, label):
        endpoint = '/Block/Label/{}'.format(id)
        payload = {'position': 0, 'label': label}
        return self.post(endpoint, payload, expected_response_code=200)


    def write_rr1727_default_sweep(self, id, points, integration_cycles, sweepType ):
        endpoint = '/Command/updateIvCurveParameters/%d' % (id)
        payload = {'points': points, 'delay': integration_cycles, 'sweepstyle': sweepType}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)


    def read_rr1727_calibration_values(self, guid):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'ReadFloatEeprom', 'Parameters': {'count': 4, 'address': 4}}
        return self.post(endpoint, payload, expected_response_code=200)['1']

    def write_rr1727_calibration_values(self, guid, A, B, C, D):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': A, 'address': 4}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': B, 'address': 8}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': C, 'address': 12}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': D, 'address': 16}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        self.reset_block(guid)

    def get_schedules(self):
        endpoint = '/Pipeline'
        return self.get(endpoint)

    def create_schedule(self, interval='* * * * *', daylightOnly=False):
        if interval == 1:
            crontab = '* * * * *'
        else:
            crontab ='*/%d * * * *' % (interval)

        description = 'Execute every %d minutes' % (interval)
        if daylightOnly:
            description += ' during daylight'

        endpoint = "/Pipeline"
        payload = {'description': description,  'daylightOnly': daylightOnly,  'cronTabs': [crontab]}
        return self.post(endpoint, payload, expected_response_code=201)

    def delete_schedule(self, id):
        endpoint = '/Pipeline/{}'.format(id)
        self.delete(endpoint)

    def enable_scheduler(self):
        endpoint = '/Pipeline/enable'
        self.post(endpoint, {}, expected_response_code=204, json_response=False)

    def disable_scheduler(self):
        endpoint = '/Pipeline/disable'
        self.post(endpoint, {}, expected_response_code=204, json_response=False)

    def update_sensor_description(self, id, label):
        endpoint = '/Sensor/{}'.format(id)
        original = self.get(endpoint)
        sensor = {'description': label,
                  'enabled': original['enabled'],
                  'unit': original['unit'],
                  'calibration': original['calibration'],
                  'options': original['options'],
                  'name': original['name'] }
        self.put(endpoint, sensor)


    def attach_sensor_to_pvdevice(self, sensor_id, pvdevice_id):
        endpoint = '/Sensor/%d/attach/%d' % (sensor_id, pvdevice_id)
        payload = {}
        self.post(endpoint, payload, expected_response_code=201)

    def add_command_to_schedule(self, schedule_id, blockId, command):
        endpoint = '/Pipeline/%d/command' % (schedule_id)
        payload = { 'pvBlockId': blockId,  'commandName': command['name'], 'parameters': command['defaultParameters'], 'withTrigger': command['defaultWithTrigger']}
        self.post(endpoint, payload, expected_response_code=201)

    # State definitions:
    # Voc = 0,
    # Isc = 1,
    # Mpp = 2,
    # Vbias = 3

    def write_rr1727_state(self, guid, state, voltageBias=0, store=True):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'ApplyState', 'Parameters': {'state': state, 'voltageBias': voltageBias}}
        self.post(endpoint, payload, expected_response_code=200)
        if store:
            endpoint = '/Hardware/%s/storeIvMppState' % (guid)
            payload = {'guid': guid, 'state': state, 'vbias': voltageBias}
            self.put(endpoint, payload, expected_response_code=201)

    def ApplyVoc(self, guid):
        self.write_rr1727_state(guid, 0, store=False)

    def ApplyIsc(self, guid):
        self.write_rr1727_state(guid, 1, store=False)

    def write_rr1727_integration_time(self, guid, integration_time):
        if integration_time not in [1,4,9,15]:
            raise ValueError("Integration time must be in [1,4,9,15]")

        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'WriteEeprom', 'Parameters': {'data': str(integration_time), 'address': 116}}
        self.post(endpoint, payload, expected_response_code=200)
        self.reset_block(guid)

    def read_rr1727_integration_time(self, guid):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'ReadEeprom', 'Parameters': {'length': 1, 'address': 116}}
        return self.post(endpoint, payload, expected_response_code=200)['1'][0]

    def read_rr1727_mpp_values(self, guid):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'ReadFloatEeprom', 'Parameters': {'count': 4, 'address': 64}}
        return self.post(endpoint, payload, expected_response_code=200)['1']

    def write_rr1727_mpp_values(self, guid, p1, p2, p3, p4):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': p1, 'address': 64}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': p2, 'address': 68}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': p3, 'address': 72}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        payload = {'CommandName': 'WriteFloatEeprom', 'Parameters': {'flt': p4, 'address': 76}}
        self.post(endpoint, payload, expected_response_code=200, json_response=False)
        endpoint = '/Hardware/%s/refresh-eeprom' % (guid)
        self.get(endpoint, expected_response_code=204, json_response=False)

    def read_rr1741_temperatures(self, guid):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'GetTemperatures', 'Parameters': {'direct': True}}
        result = self.post(endpoint, payload, expected_response_code=200)
        return [result['1']['temperature'], result['2']['temperature']]

    def read_rr1727_ivpoint(self, guid):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'MeasureDirectIvPoint'}
        result = self.post(endpoint, payload, expected_response_code=200)
        return [result['1']['ivpoint']['i'], result['1']['ivpoint']['v']]

    def sweep_rr1727_ivcurve(self, guid, points, integration_cycles, sweepType):
        endpoint = '/Hardware/%s/sendCommand' % (guid)
        payload = {'CommandName': 'StartIvCurve', 'Parameters': {'points': points, 'delay': integration_cycles, 'sweepstyle': sweepType}}
        result = self.post(endpoint, payload, expected_response_code=200)
        return {'Voltages': result['1']['Voltages'], 'Currents': result['1']['Currents']}

    def send_trigger(self):
        endpoint = '/Hardware/trigger'
        self.post(endpoint, {}, expected_response_code=200, json_response=False)