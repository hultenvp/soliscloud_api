from __future__ import annotations

import hashlib
import hmac
import base64
import asyncio
import re
import json
import async_timeout
from datetime import datetime, timezone
from http import HTTPStatus
from enum import Enum
from typing import Any
from throttler import throttle
from aiohttp import ClientError, ClientSession

SUPPORTED_SPEC_VERSION = '2.0'

VERB = "POST"
RESOURCE_PREFIX = '/v1/api/'

# Endpoints
USER_STATION_LIST = RESOURCE_PREFIX + 'userStationList'
STATION_DETAIL = RESOURCE_PREFIX + 'stationDetail'
COLLECTOR_LIST = RESOURCE_PREFIX + 'collectorList'
COLLECTOR_DETAIL = RESOURCE_PREFIX + 'collectorDetail'
COLLECTOR_DAY = RESOURCE_PREFIX + 'collector/day'
INVERTER_LIST = RESOURCE_PREFIX + 'inverterList'
INVERTER_DETAIL = RESOURCE_PREFIX + 'inverterDetail'
STATION_DAY = RESOURCE_PREFIX + 'stationDay'
STATION_MONTH = RESOURCE_PREFIX + 'stationMonth'
STATION_YEAR = RESOURCE_PREFIX + 'stationYear'
STATION_ALL = RESOURCE_PREFIX + 'stationAll'
INVERTER_DAY = RESOURCE_PREFIX + 'inverterDay'
INVERTER_MONTH = RESOURCE_PREFIX + 'inverterMonth'
INVERTER_YEAR = RESOURCE_PREFIX + 'inverterYear'
INVERTER_ALL = RESOURCE_PREFIX + 'inverterAll'
INVERTER_SHELF_TIME = RESOURCE_PREFIX + 'inverter/shelfTime'
ALARM_LIST = RESOURCE_PREFIX + 'alarmList'
STATION_DETAIL_LIST = RESOURCE_PREFIX + 'stationDetailList'
INVERTER_DETAIL_LIST = RESOURCE_PREFIX + 'inverterDetailList'
STATION_DAY_ENERGY_LIST = RESOURCE_PREFIX + 'stationDayEnergyList'
STATION_MONTH_ENERGY_LIST = RESOURCE_PREFIX + 'stationMonthEnergyList'
STATION_YEAR_ENERGY_LIST = RESOURCE_PREFIX + 'stationYearEnergyList'
EPM_LIST = RESOURCE_PREFIX + 'epmList'
EPM_DETAIL = RESOURCE_PREFIX + 'epmDetail'
EPM_DAY = RESOURCE_PREFIX + 'epm/day'
EPM_MONTH = RESOURCE_PREFIX + 'epm/month'
EPM_YEAR = RESOURCE_PREFIX + 'epm/year'
EPM_ALL = RESOURCE_PREFIX + 'epm/all'
WEATHER_LIST = RESOURCE_PREFIX + 'weatherList'
WEATHER_DETAIL = RESOURCE_PREFIX + 'weatherDetail'

ONLY_INV_ID_OR_SN_ERR = \
    "Only pass one of inverter_id or inverter_sn as identifier"
INV_SN_ERR = "Cannot parse inverter serials, pass inverter_sn as int, str or list"  # noqa: E501
ONLY_COL_ID_OR_SN_ERR = \
    "Only pass one of collector_id or collector_sn as identifier"
COL_SN_ERR = "Pass collector_sn as identifier"
ONLY_STN_ID_OR_SN_ERR = \
    "Only pass one of station_id or nmi_code as identifier"
EPM_SN_ERR = "Pass epm_sn as identifier"
PAGE_SIZE_ERR = "page_size must be <= 100"
WEATHER_SN_ERR = "Pass instrument_sn as identifier, \
containing weather instrument serial"


class SoliscloudError(Exception):
    """General exception for SolisCloud API errors."""


class SoliscloudHttpError(SoliscloudError):
    """Exception raised for HTTP errors during calls."""

    def __init__(self, statuscode, message=None):
        self.statuscode = statuscode
        if not message:
            if statuscode == 408:
                now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
                message = f"Your system time is different from server time, your time is {now}"  # noqa: E501
            else:
                message = f"Http status code: {statuscode}"
        super().__init__(message)


class SoliscloudTimeoutError(SoliscloudError):
    """Exception raised for timeouts during calls."""

    def __init__(self, message="Timeout error occurred"):
        super().__init__(message)


class SoliscloudApiError(SoliscloudError):
    """Exception raised for errors during API calls."""

    def __init__(
            self, message="Undefined API error occurred", code="Unknown",
            response=None):
        self.code = code
        self.response = response
        super().__init__(message)

    def __str__(self):
        return f'API returned an error: {self.args[0]}, error code: {self.code}, response: {self.response}'  # noqa: E501


class SoliscloudAPI():
    """Class with methods for reading data from the Soliscloud Portal.
    All methods are asynchronous and require an aiohttp ClientSession.
    Returned data is in JSON format as Python dict's."""
    DEFAULT_DOMAIN = 'https://www.soliscloud.com:13333'

    def __init__(self, domain: str, session: ClientSession) -> None:
        if domain is None:
            domain = SoliscloudAPI.DEFAULT_DOMAIN
        else:
            self._domain = domain.rstrip("/")
        self._session: ClientSession = session

    class DateFormat(Enum):
        DAY = 0
        MONTH = 1
        YEAR = 2

    @property
    def domain(self) -> str:
        """ Soliscloud domain URL.

        Returns:
            str: Soliscloud domain URL.
        """
        return self._domain

    @property
    def session(self) -> ClientSession:
        """aiohttp client session ID.

        Returns:
            ClientSession: aiohttp client session.
        """
        return self._session

    @property
    def spec_version(self) -> str:
        """Supported version of the Soliscloud spec.

        Returns:
            str: Supported version of the Soliscloud spec.
        """
        return SUPPORTED_SPEC_VERSION

    # All methods take key and secret as positional arguments followed by
    # one or more keyword arguments
    async def user_station_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """List of data of all Power stations under account. Results are paged.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Number of page to return.
                Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API containing data records\
                for all stations under account
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(
            USER_STATION_LIST, key_id, secret, params
        )

    async def station_detail(
        self, key_id: str, secret: bytes, /, *,
        station_id: int,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """Power station details

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            station_id (int, optional, keyword): Station ID. Defaults to None.
                Either station ID or NMI code must be provided
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API containing station details
        """

        params: dict[str, Any] =\
            SoliscloudAPI._precondition_station_or_nmi(station_id, nmi_code)
        return await self._get_data(STATION_DETAIL, key_id, secret, params)

    async def collector_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: int = None,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """Datalogger list. Results are paged. Returns datalogger info under
        station_id/nmi_code if given, else info for all dataloggers under
        account.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Page size. Defaults to 20.
                Max 100.
            station_id (int, optional, keyword): Station ID. Defaults to None.
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            params['stationId'] = station_id
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(COLLECTOR_LIST, key_id, secret, params)

    async def collector_detail(
        self, key_id: str, secret: bytes, /, *,
        collector_sn: int = None,
        collector_id: str = None
    ) -> dict[str, Any]:
        """Datalogger details. Returns all datalogger details for given
            serial number or datalogger ID.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            collector_sn (int, optional, keyword): Collector serial number.
                Defaults to None. Either serial number or collector ID must be
                provided.
            collector_id (str, optional, keyword): Collector ID.
                Defaults to None. Either serial number or collector ID must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        params: dict[str, Any] =\
            SoliscloudAPI._precondition_collector_id_or_sn(
                collector_id, collector_sn)
        return await self._get_data(COLLECTOR_DETAIL, key_id, secret, params)

    async def collector_day(
        self, key_id: str, secret: bytes, /, *,
        collector_sn: int = None,
        time: str,
        time_zone: int,
    ) -> dict[str, Any]:
        """Datalogger day statistics

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            time (str): Date string in format YYYY-MM-DD
            time_zone (int): Time zone offset from UTC in hours
            collector_sn (int, optional, keyword): Collector serial number.
                Defaults to None.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API containing daily statistics
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'time': time,
            'timeZone': time_zone
        }

        if (collector_sn is None):
            raise SoliscloudError(COL_SN_ERR)
        params['sn'] = collector_sn

        return await self._get_data(COLLECTOR_DAY, key_id, secret, params)

    async def inverter_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """Inverter list
        Returns data records for all inverters under station_id/nmi_code if
        given, else all inverters under account.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Page size. Defaults to 20.
                Max 100.
            station_id (str, optional, keyword): Station ID. Defaults to None.
                If neither stationID nor NMI code are provided then all
                inverters under account are returned.
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None,only for AUS. If neither stationID nor NMI code are
                provided then all inverters under account are returned.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API containing inverter list
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            # If not specified all inverters for all stations for key_id are
            # returned
            params['stationId'] = station_id
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(INVERTER_LIST, key_id, secret, params)

    async def inverter_detail(
        self, key_id: str, secret: bytes, /, *,
        inverter_sn: int = None,
        inverter_id: str = None
    ) -> dict[str, Any]:
        """Inverter details for specified inverter

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            inverter_sn (int, optional, keyword): Inverter serial number.
                Defaults to None. Either serial number or inverter ID must be
                provided.
            inverter_id (str, optional, keyword): Inverter ID. Defaults to
                None. Either serial number or inverter ID must be provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from containing details for
                specified inverter
        """
        params: dict[str, Any] = SoliscloudAPI._precondition_inverter_id_or_sn(
            inverter_id, inverter_sn)
        return await self._get_data(INVERTER_DETAIL, key_id, secret, params)

    async def station_day(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        time: str,
        time_zone: int,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, Any]:
        """Station daily graph containing records for specified day

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            time (str): Date string in format YYYY-MM-DD
            time_zone (int): Time zone offset from UTC in hours
            station_id (int, optional, keyword): Station ID. Defaults to None.
                Either station ID or NMI code must be provided
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'money': currency,
            'time': time,
            'timeZone': time_zone
        }
        id = SoliscloudAPI._precondition_station_or_nmi(station_id, nmi_code)
        params.update(id)
        return await self._get_data(STATION_DAY, key_id, secret, params)

    async def station_month(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        month: str,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, Any]:
        """Station monthly graph  containing records for specified month

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            month (str): Date string in format YYYY-MM
            station_id (int, optional, keyword): Station ID. Defaults to None.
                Either station ID or NMI code must be provided
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'money': currency, 'month': month}
        id = SoliscloudAPI._precondition_station_or_nmi(station_id, nmi_code)
        params.update(id)
        return await self._get_data(STATION_MONTH, key_id, secret, params)

    async def station_year(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        year: str,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, Any]:
        """Station yearly graph containing records for specified year

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            year (str): Date string in format YYYY
            station_id (int, optional, keyword): Station ID. Defaults to None.
                Either station ID or NMI code must be provided
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'money': currency, 'year': year}
        id = SoliscloudAPI._precondition_station_or_nmi(station_id, nmi_code)
        params.update(id)
        return await self._get_data(STATION_YEAR, key_id, secret, params)

    async def station_all(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        station_id: int = None,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """Station cumulative graph

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            station_id (int, optional, keyword): Station ID. Defaults to None.
                Either station ID or NMI code must be provided
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        params: dict[str, Any] = {'money': currency}
        id = SoliscloudAPI._precondition_station_or_nmi(station_id, nmi_code)
        params.update(id)
        return await self._get_data(STATION_ALL, key_id, secret, params)

    async def inverter_day(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        time: str,
        time_zone: int,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, Any]:
        """Inverter daily graph containing records for specified day

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            time (str): Date string in format YYYY-MM-DD
            time_zone (int): Time zone offset from UTC in hours
            inverter_id (str, optional, keyword): Inverter ID. Defaults to
                None. Either serial number or inverter ID must be provided.
            inverter_sn (int, optional, keyword): Inverter serial number.
                Defaults to None. Either serial number or inverter ID must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'money': currency,
            'time': time,
            'timeZone': time_zone
        }
        id = SoliscloudAPI._precondition_inverter_id_or_sn(
            inverter_id, inverter_sn)
        params.update(id)
        return await self._get_data(INVERTER_DAY, key_id, secret, params)

    async def inverter_month(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        month: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, Any]:
        """Inverter monthly graph containing records for specified month

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            month (str): Date string in format YYYY-MM
            inverter_id (str, optional, keyword): Inverter ID. Defaults to
                None. Either serial number or inverter ID must be provided.
            inverter_sn (int, optional, keyword): Inverter serial number.
                Defaults to None. Either serial number or inverter ID must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'money': currency, 'month': month}

        id = SoliscloudAPI._precondition_inverter_id_or_sn(
            inverter_id, inverter_sn)
        params.update(id)
        return await self._get_data(INVERTER_MONTH, key_id, secret, params)

    async def inverter_year(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        year: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, Any]:
        """Inverter yearly graph containing records for specified year

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            year (str): Date string in format YYYY
            inverter_id (str, optional, keyword): Inverter ID. Defaults to
                None. Either serial number or inverter ID must be provided.
            inverter_sn (int, optional, keyword): Inverter serial number.
                Defaults to None. Either serial number or inverter ID must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'money': currency, 'year': year}
        id = SoliscloudAPI._precondition_inverter_id_or_sn(
            inverter_id, inverter_sn)
        params.update(id)
        return await self._get_data(INVERTER_YEAR, key_id, secret, params)

    async def inverter_all(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, Any]:
        """The cumulative chart for the corresponding inverter.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            currency (str): Currency code, e.g. "USD"
            inverter_id (str, optional, keyword): Inverter ID. Defaults to
                None. Either serial number or inverter ID must be provided.
            inverter_sn (int, optional, keyword): Inverter serial number.
                Defaults to None. Either serial number or inverter ID must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        params: dict[str, Any] = {'money': currency}
        id = SoliscloudAPI._precondition_inverter_id_or_sn(
            inverter_id, inverter_sn)
        params.update(id)
        return await self._get_data(INVERTER_ALL, key_id, secret, params)

    async def inverter_shelf_time(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        inverter_sn: str = None
    ) -> dict[str, Any]:
        """Inverter warranty information

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.
            inverter_sn (Any, optional, keyword): One or inverter serial
                numbers. Defaults to None.
                Accepts: int, str, list[int], list[str]
                in case of string the serial numbers should be comma-separated.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {
            'pageNo': page_no,
            'pageSize': page_size}
        sn = ""
        if type(inverter_sn) is int:
            sn = str(inverter_sn)
        elif type(inverter_sn) is str:
            sn = inverter_sn
        elif isinstance(inverter_sn, list):
            sn = ",".join(str(i) for i in inverter_sn)
        else:
            raise SoliscloudError(INV_SN_ERR)
        if inverter_sn is not None:
            params['sn'] = sn
        return await self._get_records(
            INVERTER_SHELF_TIME, key_id, secret, params)

    async def alarm_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None,
        device_sn: str = None,
        begintime: str = None,
        endtime: str = None,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """Alarm check

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.
            station_id (int, optional, keyword): Station ID. Defaults to None.
            device_sn (str, optional, keyword): Device serial number.
                Defaults to None.
            begintime (str, optional, keyword): Start date format YYYY-MM-DD.
                Defaults to None.
            endtime (str, optional, keyword): End date format YYYY-MM-DD.
                Defaults to None.
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None and device_sn is None:
            params['stationId'] = station_id
        elif station_id is None and device_sn is not None:
            params['alarmDeviceSn'] = device_sn
        else:
            raise SoliscloudError(
                "Only pass one of station_id or device_sn as identifier")
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, begintime)
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, endtime)
        params['alarmBeginTime'] = begintime
        params['alarmEndTime'] = endtime
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(ALARM_LIST, key_id, secret, params)

    async def station_detail_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Batch acquire station details of all stations under account.
        Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        return await self._get_records(
            STATION_DETAIL_LIST, key_id, secret, params)

    async def inverter_detail_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Batch acquire inverter details of all inverters under account.
        Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        return await self._get_records(
            INVERTER_DETAIL_LIST, key_id, secret, params)

    async def station_day_energy_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        time: str
    ) -> dict[str, Any]:
        """Batch acquire station daily generation of all stations under
        account. Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            time (str): Date string in format YYYY-MM-DD
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
            Max 100.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'pageNo': page_no,
            'pageSize': page_size,
            'time': time
        }

        return await self._get_records(
            STATION_DAY_ENERGY_LIST, key_id, secret, params)

    async def station_month_energy_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        month: str
    ) -> dict[str, Any]:
        """Batch acquire station monthly generation of all stations under
        account. Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            month (str): Date string in format YYYY-MM
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {
            'pageNo': page_no,
            'pageSize': page_size,
            'time': month
        }

        return await self._get_records(
            STATION_MONTH_ENERGY_LIST, key_id, secret, params)

    async def station_year_energy_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        year: str
    ) -> dict[str, Any]:
        """Batch acquire station yearly generation of all stations under
        account. Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            year (str): Date string in format YYYY
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {
            'pageNo': page_no,
            'pageSize': page_size,
            'time': year
        }

        return await self._get_records(
            STATION_YEAR_ENERGY_LIST, key_id, secret, params)

    async def epm_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None
    ) -> dict[str, Any]:
        """List of all EPMs for given station ID or all EPMs under account.
        Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.
            station_id (int, optional, keyword): Station ID. Defaults to None.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            params['stationId'] = station_id

        return await self._get_records(EPM_LIST, key_id, secret, params)

    async def epm_detail(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str
    ) -> dict[str, Any]:
        """EPM details for given EPM serial number

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            epm_sn (str): Serial number of EPM

        Returns:
            dict[str, Any]: JSON response from API
        """
        if not epm_sn:
            raise SoliscloudError(EPM_SN_ERR)
        params: dict[str, Any] = {'sn': epm_sn}

        return await self._get_data(EPM_DETAIL, key_id, secret, params)

    async def epm_day(
        self, key_id: str, secret: bytes, /, *,
        searchinfo: str,
        epm_sn: str,
        time: str,
        time_zone: int
    ) -> dict[str, Any]:
        """EPM daily graph

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            searchinfo (str): Query fields, separated by commas for
                multiple queries:
                * u_ac1=VoltageU
                * u_ac2=VoltageV
                * u_ac3=VoltageW
                * i_ac1=CurrentU
                * i_ac2=CurrentV
                * i_ac3=currentW
                * p_ac1=PowerU
                * p_ac2=PowerV
                * p_ac3=powerW
                * power_factor=grid power factor
                * fac_meter=Grid frequency(Meter)
                * p_load=total power of the load
                * e_total_inverter=total output of the inverter
                * e_total_load=total power consumption of the load
                * e_total_buy=total electricity purchased
                * e_total_sell=total electricity sold
            epm_sn (str): Serial number of EPM
            time (str): Date string in format YYYY-MM-DD
            time_zone (int): Time zone offset from UTC in hours

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'searchinfo': searchinfo,
            'sn': epm_sn,
            'time': time,
            'timezone': time_zone}

        return await self._get_data(EPM_DAY, key_id, secret, params)

    async def epm_month(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str,
        month: str,
    ) -> dict[str, Any]:
        """EPM monthly graph

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            epm_sn (str): Serial number of EPM
            month (str): Date string in format YYYY-MM

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'sn': epm_sn, 'month': month}

        return await self._get_data(EPM_MONTH, key_id, secret, params)

    async def epm_year(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str,
        year: str
    ) -> dict[str, Any]:
        """EPM yearly graph

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            epm_sn (str): Serial number of EPM
            year (str): Date string in format YYYY

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'sn': epm_sn, 'year': year}

        return await self._get_data(EPM_YEAR, key_id, secret, params)

    async def epm_all(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str
    ) -> dict[str, Any]:
        """EPM cumulative graph

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            epm_sn (str): Serial number of EPM

        Returns:
            dict[str, Any]: JSON response from API
        """
        params: dict[str, Any] = {'sn': epm_sn}

        return await self._get_data(EPM_ALL, key_id, secret, params)

    async def weather_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None,
        nmi_code: str = None
    ) -> dict[str, Any]:
        """List of weather data records per station. Returns records for all
        stations under station_id/nmi_code if given, else all stations under
        account. 'id' in each record is instrument ID. Paged results.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            page_no (int, optional, keyword): Page number. Defaults to 1.
            page_size (int, optional, keyword): Size of page. Defaults to 20.
                Max 100.
            station_id (int, optional, keyword): Station ID. Defaults to None.
            nmi_code (str, optional, keyword): NMI code for AUS. Defaults to
                None, only for AUS. Either station ID or NMI code must be
                provided.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        SoliscloudAPI._precondition_page_size(page_size)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            params['stationId'] = station_id
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(WEATHER_LIST, key_id, secret, params)

    async def weather_detail(
        self, key_id: str, secret: bytes, /, *,
        instrument_sn: str = None
    ) -> dict[str, Any]:
        """Weather details for given instrument SN.

        Args:
            key_id (str): API key ID
            secret (bytes): API secret
            instrument_sn (str, optional, keyword): Instrument serial. Spec is
                unclear, but it looks like instrument_sn is equal to
                collector_sn. Defaults to None.

        Raises:
            SoliscloudError: Any error during call

        Returns:
            dict[str, Any]: JSON response from API
        """
        params: dict[str, Any] = {}
        if instrument_sn is None:
            raise SoliscloudError(WEATHER_SN_ERR)
        params['sn'] = instrument_sn

        return await self._get_data(WEATHER_DETAIL, key_id, secret, params)

    async def _get_records(
        self, canonicalized_resource: str, key_id: str, secret: bytes,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """API call that returns records

        Args:
            canonicalized_resource (str): API endpoint without domain
            key_id (str): API key ID
            secret (bytes): API secret
            params (dict[str, Any]): dict of parameters

        Raises:
            SoliscloudApiError: Any error during call.

        Returns:
            dict[str, Any]: return JSON records from API call
        """
        header: dict[str, str] = SoliscloudAPI._prepare_header(
            key_id, secret, params, canonicalized_resource)

        url = f"{self.domain}{canonicalized_resource}"
        try:
            result = await self._post_data_json(url, header, params)
            if 'page' in result.keys():
                return result['page']['records']
            else:
                return result['records']
        except KeyError as err:
            raise SoliscloudApiError("Malformed data", result) from err

    async def _get_data(
        self, canonicalized_resource: str, key_id: str, secret: bytes,
        params: dict[str, Any]
    ):
        """API call that returns one record

        Args:
            canonicalized_resource (str): API endpoint without domain
            key_id (str): API key ID
            secret (bytes): API secret
            params (dict[str, Any]): dict of parameters

        Returns:
            dict[str, Any]: return JSON data from API call
        """
        header: dict[str, str] = SoliscloudAPI._prepare_header(
            key_id, secret, params, canonicalized_resource)

        url = f"{self.domain}{canonicalized_resource}"
        result = await self._post_data_json(url, header, params)

        return result

    @staticmethod
    def _now() -> datetime.datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _prepare_header(
        key_id: str,
        secret: bytes,
        body: dict[str, str],
        canonicalized_resource: str
    ) -> dict[str, str]:
        content_md5 = base64.b64encode(
            hashlib.md5(json.dumps(body, separators=(
                ",", ":")).encode('utf-8')).digest()
        ).decode('utf-8')

        content_type = "application/json"

        date = SoliscloudAPI._now().strftime("%a, %d %b %Y %H:%M:%S GMT")

        encrypt_str = (
            VERB + "\n"
            + content_md5 + "\n"
            + content_type + "\n"
            + date + "\n"
            + canonicalized_resource
        )
        hmac_obj = hmac.new(
            secret,
            msg=encrypt_str.encode('utf-8'),
            digestmod=hashlib.sha1
        )
        sign = base64.b64encode(hmac_obj.digest())
        authorization = "API " + key_id + ":" + sign.decode('utf-8')

        header: dict[str, str] = {
            "Content-MD5": content_md5,
            "Content-Type": content_type,
            "Date": date,
            "Authorization": authorization
        }
        return header

    @throttle(rate_limit=2, period=1.0)
    async def _post_data_json(
        self,
        url: str,
        header: dict[str, Any],
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """ Http-post data to specified domain/canonicalized_resource. """

        resp = None
        result = None
        if self._session is None:
            raise SoliscloudError(
                "aiohttp.ClientSession not set")
        try:
            async with async_timeout.timeout(10):
                resp = await SoliscloudAPI._do_post_aiohttp(
                    self._session, url, params, header)

                result = await resp.json()
                if resp.status == HTTPStatus.OK:
                    if result['code'] != '0':
                        raise SoliscloudApiError(
                            result['msg'], result['code'])
                    return result['data']
                else:
                    raise SoliscloudHttpError(resp.status)
        except asyncio.TimeoutError as err:
            if resp is not None:
                await resp.release()
            raise SoliscloudTimeoutError() from err
        except ClientError as err:
            if resp is not None:
                await resp.release()
            raise SoliscloudApiError(err)
        except (KeyError, TypeError) as err:
            raise SoliscloudApiError(
                "Malformed server response", response=result) from err

    @staticmethod
    async def _do_post_aiohttp(
        session,
        url: str,
        params: dict[str, Any],
        header: dict[str, Any]
    ) -> dict[str, Any]:
        """ Allows mocking for unit tests."""
        return await session.post(url, json=params, headers=header)

    @staticmethod
    def _verify_date(format: SoliscloudAPI.DateFormat, date: str):
        rex = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
        err = SoliscloudError(
            "time must be in format YYYY-MM-DD")
        if format == SoliscloudAPI.DateFormat.MONTH:
            rex = re.compile("^[0-9]{4}-[0-9]{2}$")
            err = SoliscloudError(
                "month must be in format YYYY-MM")
        elif format == SoliscloudAPI.DateFormat.YEAR:
            rex = re.compile("^[0-9]{4}$")
            err = SoliscloudError("year must be in format YYYY")
        if not rex.match(date):
            raise err
        return

    @staticmethod
    def _precondition_station_or_nmi(station_id: int, nmi_code: str):
        params: dict[str, Any] = {}
        if (station_id is not None and nmi_code is None):
            params['id'] = station_id
        elif (station_id is None and nmi_code is not None):
            params['nmiCode'] = nmi_code
        else:
            raise SoliscloudError(ONLY_STN_ID_OR_SN_ERR)
        return params

    @staticmethod
    def _precondition_page_size(page_size: int):
        if page_size > 100:
            raise SoliscloudError(PAGE_SIZE_ERR)
        return

    @staticmethod
    def _precondition_inverter_id_or_sn(inverter_id: str, inverter_sn: int):
        params: dict[str, Any] = {}
        if (inverter_sn is not None and inverter_id is None):
            params['sn'] = inverter_sn
        elif (inverter_sn is None and inverter_id is not None):
            params['id'] = inverter_id
        else:
            raise SoliscloudError(ONLY_INV_ID_OR_SN_ERR)
        return params

    def _precondition_collector_id_or_sn(collector_id: str, collector_sn: int):
        params: dict[str, Any] = {}
        if (collector_sn is not None and collector_id is None):
            params['sn'] = collector_sn
        elif (collector_sn is None and collector_id is not None):
            params['id'] = collector_id
        else:
            raise SoliscloudError(ONLY_COL_ID_OR_SN_ERR)
        return params
