from pvblocks import pvblocks_api
from datetime import datetime, timezone

host = '100.110.124.61' #ip address of pvblocks system
apikey = 'bc3e9db9-c249-4dd6-a631-927ec85d8bdd' #API key as found in Data/PVBlocks API

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi(host ,apikey)
pvblocks.Init()

utc_now = datetime.now(timezone.utc)
formatted_time = utc_now.strftime("%Y-%m-%d %H:%M:%S")
print(f"set time to: {formatted_time}")
endpoint = f'/Host/time?time={formatted_time}'
payload = {}
pvblocks.post(endpoint, payload, expected_response_code=200, json_response=False)