"""Example application."""
import asyncio
import logging
import json

from aiohttp import ClientError, ClientSession

from soliscloud_api import SoliscloudAPI

API_KEY = "xxxxx"
# Secret needs to be a binary string!
API_SECRET = b'yyyyyyyy'
API_NMI = "zzzzz"

logging.basicConfig(level=logging.DEBUG)


async def main():
    """Run main function."""
    async with ClientSession() as websession:
        try:
            # Retrieves list of Stations, a.k.a. plants, containing the inverters.
            soliscloud = SoliscloudAPI('https://soliscloud.com:13333', websession)
            station_list = await soliscloud.user_station_list(API_KEY, API_SECRET, page_no=1, page_size=100)
            # Australian accounts require NMI, use this call instead of previous if required.
            # station_list = await soliscloud.user_station_list(KEY, SECRET, page_no=1, page_size=100, nmi_code=API_NMI)
            station_list_json = json.dumps(station_list, indent = 2)
        except (
            SoliscloudAPI.SolisCloudError,
            SoliscloudAPI.HttpError,
            SoliscloudAPI.TimeoutError,
            SoliscloudAPI.ApiError,
        ) as error:
            print(f"Error: {error}")
        else:
            print(f"UserStationList call success:")
            print(f"{station_list_json}")


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
