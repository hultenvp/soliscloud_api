"""
Example application.
Demonstrates the use of entity classes as a higher level interface to the
Soliscloud API. Fill in your own API key and secret in config.json before
running.
By using the entity classes you can more easily access the data
attributes of the plant, inverters and collectors.

There are 2 ways to create the entity classes:
1. Use the class method 'initialize_from_data' to create entity instances
   from data retrieved from the API. It will create one or more entity
   instances from the data passed in. This method will not retrieve any data
   from the API, so you need to do that yourself first. It will not
   recursively create all entities, i.e. plants, inverters and collectors.
   You need to call it separately for each entity class.
2. Use the class method 'initialize_from_session' to create entity instances
   by passing in the aiohttp session and API credentials. This method will
   retrieve the data from the API and create the entity instances. It
   will recursively create all entities, i.e. plants, inverters
   and collectors when called on the Plant class and inverters and collectors
   when called on the Inverter class.
"""
from __future__ import annotations

import asyncio
import logging
import json

from aiohttp import ClientSession

from soliscloud_api import SoliscloudError, SoliscloudHttpError, \
    SoliscloudTimeoutError, SoliscloudApiError
from soliscloud_api import Plant, Inverter, Collector  # noqa: F401
from soliscloud_api import SoliscloudAPI as api


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
            the_api = api('https://soliscloud.com:13333', websession)
            data = await the_api.inverter_list(
                api_key, api_secret, page_no=1, page_size=100)
            # use plant_id of your own plant here to get inverters for that plant
            # use inverter_id to only get one specific inverter
            inverters = Inverter.initialize_from_data(
                data, plant_id='your plant id goes here')
            plants = await Plant.initialize_from_session(
                websession, api_key, api_secret)
        except (
            SoliscloudError,
            SoliscloudHttpError,
            SoliscloudTimeoutError,
            SoliscloudApiError,
        ) as error:
            print(f"Error: {error}")
        else:
            p = plants[0]
            print(f"Plant id: {p.plant_id}")
            print(f"Plant name: {p.data['station_name']}")
            print(f"Number of inverters: {len(p.inverters)}")
            for inv in inverters:
                print(f"Inverter id: {inv.inverter_id}")
                # The attributes if the inverter are in inv.data
                # If an attribute has a unit then the value is of
                # dimensioned type
                print(f"Total energy: {inv.data['etotal']}")
                print(f"Total energy value: {inv.data['etotal'].value}")
                print(f"Total energy unit: {inv.data['etotal'].unit}")
loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
