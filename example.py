"""
Example application.
Demonstrates usage of the SoliscloudAPI class to interact with the Soliscloud
API. It also shows how to use the Helpers class for common tasks.
Fill in your own API key and secret in config.json before running.
"""

import asyncio
import logging
import json

from aiohttp import ClientSession

from soliscloud_api import SoliscloudAPI, SoliscloudError, \
    SoliscloudHttpError, SoliscloudTimeoutError, SoliscloudApiError, \
    Helpers


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

            # Retrieve list of Stations, a.k.a. plants
            station_list = await soliscloud.user_station_list(
                api_key, api_secret, page_no=1, page_size=100,
                # Australian accounts require nmi, uncomment if required.
                # (NOT TESTED!)
                # nmi_code=api_nmi
            )
            station_list_json = json.dumps(station_list, indent=2)
            # Use helper class as alternative to directly retrieve station id's
            station_ids = await Helpers.get_station_ids(
                soliscloud, api_key, api_secret)

            # Get inverter data for all stations
            inverter_list = await soliscloud.inverter_list(
                api_key, api_secret, page_no=1, page_size=100,
                # Australian accounts require nmi, uncomment if required.
                # (NOT TESTED!)
                # nmi_code=api_nmi
            )
            inverter_list_json = json.dumps(inverter_list, indent=2)
            # Use helper class to retrieve all inverter id's
            inverter_ids = Helpers.get_inverter_ids_from_response(
                inverter_list)

            # Get detailed data for all inverters
            idl = await soliscloud.inverter_detail_list(api_key, api_secret)
            idl_json = json.dumps(idl, indent=2)

            # Use serial number of first inverter to get details
            # (should be same as first in inverter_list)
            inverter_x = await soliscloud.inverter_detail(
                api_key, api_secret, inverter_sn=inverter_list[0]['sn'])
            inverter_detail_json = json.dumps(inverter_x, indent=2)

            # Get data collectors for all stations
            collector_list = await soliscloud.collector_list(
                api_key, api_secret, page_no=1, page_size=100,
                # Australian accounts require nmi, uncomment if required.
                # (NOT TESTED!)
                # nmi_code=api_nmi
            )
            collector_list_json = json.dumps(collector_list, indent=2)

        except (
            SoliscloudError,
            SoliscloudHttpError,
            SoliscloudTimeoutError,
            SoliscloudApiError,
        ) as error:
            print(f"Error: {error}")
        else:
            print("UserStationList call success:")
            print(f"{station_list_json}")

            print("Helper call success:")
            print(f"{station_ids}")

            print("InverterList call success:")
            print(f"{inverter_list_json}")

            print("InverterDetails call success:")
            print(inverter_detail_json)
            for key in ['iA', 'uA', 'pA', 'iB', 'uB', 'pB', 'iC', 'uC', 'pC']:
                print(f"{key}: {inverter_x[key]}")

            print("Helper call success:")
            print(f"{inverter_ids}")

            print("CollectorList call success:")
            print(f"{collector_list_json}")

            print("InverterDetailList call success:")
            print(idl_json)
            for key in [
                'iAc1',
                'uAc1',
                'pA',
                'iB',
                'uB',
                'pB',
                'iC',
                'uC',
                'pC',
                'apparentPower'
            ]:
                print(f"{key}: {idl[0][key]}")

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
