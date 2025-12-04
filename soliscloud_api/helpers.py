"""Helper class

For more information: https://github.com/hultenvp/soliscloud_api
"""
from __future__ import annotations
from typing import Any

from soliscloud_api import SoliscloudAPI, SoliscloudError


class Helpers():

    @staticmethod
    async def get_station_ids(
        api: SoliscloudAPI, key_id: str, secret: bytes,
        nmi: str = None
    ) -> tuple[int]:
        """Calls user_station_list and returns all station id's from the
        response.
        If nmi is given then the nmi_code parameter is used in the call
        (Australian accounts require nmi)

        Args:
            api (SoliscloudAPI): instance of SoliscloudAPI
            key (str): API key
            secret (bytes): API secret
            nmi (str, optional): NMI code for AUS. Defaults to None.

        Returns:
            tuple[int]: tuple of Station IDs or None on error
        """
        try:
            response = await api.user_station_list(
                key_id, secret, page_no=1, page_size=100, nmi_code=nmi)
            return Helpers.get_station_ids_from_response(response)
        except SoliscloudError:
            return None

    @staticmethod
    def get_station_ids_from_response(
        response: dict[str, Any],
    ) -> tuple[int]:
        """Takes response from user_station_list and returns all station id's
        from the response as a tuple of int's.

        Args:
            response (dict[str, Any]): api response from user_station_list

        Returns:
            tuple[int]: tuple of Station IDs
        """
        if response is None:
            return None
        stations = ()
        for element in response:
            try:
                stations = stations + (int(element['id']),)
            except KeyError:
                continue
        return stations

    @staticmethod
    async def get_inverter_ids(
        api: SoliscloudAPI, key_id: str, secret: bytes,
        station_id: int = None,
        nmi: str = None
    ) -> tuple[int]:
        """Calls inverter_list and returns all inverter id's from response as a
        tuple of int's or None on error.
        (Australian accounts require nmi)

        is returned, else all inverter id's for all stations

        Args:
            api (SoliscloudAPI): instance of SoliscloudAPI
            key (str): API key
            secret (bytes): API secret
            station_id (int, optional): If a station_id is given then a list
                of inverters for that station_id. Defaults to None.
            nmi (str, optional): NMI code for AUS. Defaults to None.

        Returns:
            tuple[int]: tuple of Inverter IDs or None on error
        """
        try:
            response = await api.inverter_list(
                key_id, secret, page_no=1, page_size=100,
                station_id=station_id, nmi_code=nmi)
            return Helpers.get_inverter_ids_from_response(response)
        except SoliscloudError:
            return None

    @staticmethod
    def get_inverter_ids_from_response(
        response: dict[str, str],
    ) -> tuple[int]:
        """
        Takes response from inverter_list and returns all inverter id's from
        response as a tuple of int's.
        If a station_id is given then a list of inverters for that station_id
        is returned, else all inverter id's for all stations
        Args:
            response (dict[str, str]): api response from inverter_list
        Returns:
            tuple[int]: tuple of Inverter IDs
        """
        if response is None:
            return None
        inverters = ()
        for element in response:
            try:
                inverters = inverters + (int(element['id']),)
            except KeyError:
                continue
        return inverters
