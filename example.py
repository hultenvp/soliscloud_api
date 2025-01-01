"""Example application."""
import asyncio
import logging
import json

from aiohttp import ClientSession

from soliscloud_api import SoliscloudAPI
from soliscloud_api.helpers import Helpers


logging.basicConfig(level=logging.DEBUG)


async def main():
    """Run main function."""
    # Put your own key and secret in the config.json file
    with open('config.json', 'r') as file:
        data = json.load(file)

    api_key = data['key']
    api_secret = bytearray(data['secret'], 'utf-8')
    # Australian accounts require nmi, uncomment if required.
    # (NOT TESTED!)
    # api_nmi = data['nmi']

    async with ClientSession() as websession:
        try:
            soliscloud = SoliscloudAPI(
                'https://soliscloud.com:13333', websession)

            # Retrieves list of Stations, a.k.a. plants,
            # containing the inverters.
            station_list = await soliscloud.user_station_list(
                api_key, api_secret, page_no=1, page_size=100)
            # Australian accounts require nmi, uncomment if required.
            # (NOT TESTED!)
            # station_list = await soliscloud.user_station_list(
            #     api_key, api_secret, page_no=1,
            #     page_size=100, nmi_code=api_nmi)
            station_list_json = json.dumps(station_list, indent=2)
            # Use helper class as alternative
            station_ids = await Helpers.get_station_ids(
                soliscloud, api_key, api_secret)

            # Get inverters for all stations
            inverter_list = await soliscloud.inverter_list(
                api_key, api_secret, page_no=1, page_size=100)
            # Australian accounts require nmi, uncomment if required.
            # (NOT TESTED!)
            # inverter_list = await soliscloud.inverter_list(
            #     api_key, api_secret, page_no=1,
            #     page_size=100, nmi_code=api_nmi)
            inverter_list_json = json.dumps(inverter_list, indent=2)
            # Use helper class as alternative
            inverter_ids = await Helpers.get_inverter_ids(
                soliscloud, api_key, api_secret)
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
