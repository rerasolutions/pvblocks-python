from pvblocks import pvblocks_api

host = '111.111.111.111' #ip address of pvblocks system
apikey = 'aaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' #API key as found in Data/PVBlocks API
interval_in_minutes = 6
only_during_daylight = True

print(pvblocks_api.show_version())
pvblocks = pvblocks_api.PvBlocksApi(host ,apikey)
pvblocks.Init()

# Before adding a schedule to the system, it must be disabled
pvblocks.disable_scheduler()

# create schedule
pvblocks.create_schedule(interval_in_minutes, only_during_daylight)