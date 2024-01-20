"""Example application."""
import asyncio
import logging
import json
import time

from aiohttp import ClientSession

from soliscloud_api import SoliscloudAPI
from soliscloud_api.helpers import Helpers


API_KEY = "xxxxx"
# Secret needs to be a binary string!
API_SECRET = b'yyyyyyyy'
API_NMI = "zzzzz"

logging.basicConfig(level=logging.DEBUG)


async def main():
    """Run main function."""
    async with ClientSession() as websession:
        try:
            soliscloud = SoliscloudAPI('https://soliscloud.com:13333', websession)

            # Retrieves list of Stations, a.k.a. plants, containing the inverters.
            station_list = await soliscloud.user_station_list(API_KEY, API_SECRET, page_no=1, page_size=100)
            # Australian accounts require NMI, uncomment if required.
            # station_list = await soliscloud.user_station_list(KEY, SECRET, page_no=1, page_size=100, nmi_code=API_NMI)
            station_list_json = json.dumps(station_list, indent=2)
            # Use helper class as alternative
            station_ids = await Helpers.get_station_ids(soliscloud, API_KEY, API_SECRET)
            # Avoid HTTP Error 429 and limit calls/sec (see issue 8)
            time.sleep(2)

            # Get inverters for all stations
            inverter_list = await soliscloud.inverter_list(API_KEY, API_SECRET, page_no=1, page_size=100)
            # Australian accounts require NMI, uncomment if required.
            # inverter_list = await soliscloud.inverter_list(API_KEY, API_SECRET, page_no=1, page_size=100, nmi_code=API_NMI)
            inverter_list_json = json.dumps(inverter_list, indent=2)
            # Use helper class as alternative
            inverter_ids = await Helpers.get_inverter_ids(soliscloud, API_KEY, API_SECRET)
        except (
            SoliscloudAPI.SolisCloudError,
            SoliscloudAPI.HttpError,
            SoliscloudAPI.TimeoutError,
            SoliscloudAPI.ApiError,
        ) as error:
            print(f"Error: {error}")
        else:
            print("UserStationList call success:")
            print(f"{station_list_json}")

            print("Helper call success:")
            print(f"{station_ids}")

            print("InverterList call success:")
            print(f"{inverter_list_json}")

            print("Helper call success:")
            print(f"{inverter_ids}")

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
