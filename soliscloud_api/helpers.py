"""Helper class

For more information: https://github.com/hultenvp/soliscloud_api
"""
from __future__ import annotations

from soliscloud_api import SoliscloudAPI


class Helpers():

    @staticmethod
    async def get_station_ids(
        api: SoliscloudAPI, key, secret,
        nmi=None
    ) -> tuple:
        """
        Parses response from get_station_list and returns all station id's
        """
        response = await api.user_station_list(
            key, secret, page_no=1, page_size=100, nmi_code=nmi)
        stations = ()
        for element in response:
            stations = stations + (int(element['id']),)
        return stations

    @staticmethod
    async def get_inverter_ids(
        api: SoliscloudAPI, key, secret,
        station_id: int = None,
        nmi=None
    ) -> tuple:
        """
        Parses response from get_inverter_list and returns all inverter id's
        If a station_id is given then a list of inverters for that station_id
        is returned, else all inverter id's for all stations
        """
        response = await api.inverter_list(
            key, secret, page_no=1, page_size=100,
            station_id=station_id, nmi_code=nmi)
        inverters = ()
        for element in response:
            inverters = inverters + (int(element['id']),)
        return inverters
