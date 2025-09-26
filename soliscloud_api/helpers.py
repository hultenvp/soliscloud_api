"""Helper class

For more information: https://github.com/hultenvp/soliscloud_api
"""
from __future__ import annotations

from soliscloud_api import SoliscloudAPI, SoliscloudError


class Helpers():

    @staticmethod
    async def get_station_ids(
        api: SoliscloudAPI, key, secret,
        nmi=None
    ) -> tuple:
        """
        Calls user_station_list and returns all station id's from the response
        as a tuple of int's or None on error.
        If nmi is given then the nmi_code parameter is used in the call
        (Australian accounts require nmi)
        """
        try:
            response = await api.user_station_list(
                key, secret, page_no=1, page_size=100, nmi_code=nmi)
            return Helpers.get_station_ids_from_response(response)
        except SoliscloudError:
            return None

    @staticmethod
    def get_station_ids_from_response(
        response: dict[str, str],
    ) -> tuple:
        """
        Takes response from user_station_list and returns all station id's
        from the response as a tuple of int's.
        """
        if response is None:
            return None
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
        Calls inverter_list and returns all inverter id's from response as a
        tuple of int's or None on error.
        (Australian accounts require nmi)
        If a station_id is given then a list of inverters for that station_id
        is returned, else all inverter id's for all stations
        """
        try:
            response = await api.inverter_list(
                key, secret, page_no=1, page_size=100,
                station_id=station_id, nmi_code=nmi)
            return Helpers.get_inverter_ids_from_response(response)
        except SoliscloudError:
            return None

    @staticmethod
    def get_inverter_ids_from_response(
        response: dict[str, str],
    ) -> tuple:
        """
        Takes response from inverter_list and returns all inverter id's from
        response as a tuple of int's.
        If a station_id is given then a list of inverters for that station_id
        is returned, else all inverter id's for all stations
        """
        if response is None:
            return None
        inverters = ()
        for element in response:
            inverters = inverters + (int(element['id']),)
        return inverters
