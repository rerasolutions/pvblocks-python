from . import VERSION
from . import exceptions
from . import constants

import requests

EndOfLine = '\r\n'

def show_version():
    return VERSION

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
        else:
            print('System not online')

    def get_pvdevices(self):
        endpoint = '/PvDevice'
        resp = requests.get(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != 200:
            self.token = self.get_token()
            resp = requests.get(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != 200:
            raise Exception('GET /' + endpoint + '{}'.format(resp.status_code))
        else:
            return resp.json()

    def get_pvblocks(self):
        endpoint = '/Block'
        resp = requests.get(self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != 200:
            self.token = self.get_token()
            resp = requests.get(
                self._url(endpoint), headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != 200:
            raise Exception('GET /' + endpoint + '{}'.format(resp.status_code))
        else:
            return resp.json()

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
            self.Blocks.append({"guid": b['uniqueIdentifier'],
                                             "type": b['type']})

        return module_count