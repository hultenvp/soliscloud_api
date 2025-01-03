"""Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/soliscloud_api
"""
from __future__ import annotations

import hashlib
import hmac
import base64
import asyncio
import re
from datetime import datetime
from datetime import timezone
from enum import Enum
from http import HTTPStatus
import json
from typing import Any
from throttler import throttle
from aiohttp import ClientError, ClientSession
import async_timeout

# VERSION
VERSION = '1.1.0'
SUPPORTED_SPEC_VERSION = '2.0'
RESOURCE_PREFIX = '/v1/api/'

VERB = "POST"

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
INV_SN_ERR = "Pass inverter_sn as identifier"
ONLY_COL_ID_OR_SN_ERR = \
    "Only pass one of collector_id or collector_sn as identifier"
COL_SN_ERR = "Pass collector_sn as identifier"
ONLY_STN_ID_OR_SN_ERR = \
    "Only pass one of station_id or nmi_code as identifier"
PAGE_SIZE_ERR = "page_size must be <= 100"
WEATHER_SN_ERR = "Pass instrument_sn as identifier, \
containing weather instrument serial"


class SoliscloudAPI():
    """Class with functions for reading data from the Soliscloud Portal."""

    class SolisCloudError(Exception):
        """
        Exception raised for timeouts during calls.
        """

        def __init__(self, message="SolisCloud API error"):

            self.message = message
            super().__init__(self.message)

    class HttpError(SolisCloudError):
        """
        Exception raised for HTTP errors during calls.
        """

        def __init__(self, statuscode, message=None):
            self.statuscode = statuscode
            self.message = message
            if not message:
                if statuscode == 408:
                    now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
                    self.message = f"Your system time is different from \
server time, your time is {now}"
                else:
                    self.message = f"Http status code: {statuscode}"
            super().__init__(self.message)

    class TimeoutError(SolisCloudError):
        """
        Exception raised for timeouts during calls.
        """

        def __init__(self, message="Timeout error occurred"):

            self.message = message
            super().__init__(self.message)

    class ApiError(SolisCloudError):
        """
        Exception raised for errors during API calls.
        """

        def __init__(
            self,
            message="Undefined API error occurred",
            code="Unknown",
            response=None
        ):

            self.message = message
            self.code = code
            self.response = response
            super().__init__(self.message)

        def __str__(self):
            return f'API returned an error: {self.message}, \
error code: {self.code}, response: {self.response}'

    def __init__(self, domain: str, session: ClientSession) -> None:
        self._domain = domain.rstrip("/")
        self._session: ClientSession = session

    class DateFormat(Enum):
        DAY = 0
        MONTH = 1
        YEAR = 2

    @property
    def domain(self) -> str:
        """ Domain name."""
        return self._domain

    @property
    def session(self) -> ClientSession:
        """ aiohttp client session ID."""
        return self._session

    @property
    def spec_version(self) -> str:
        """ supported version of the Soliscloud spec."""
        return SUPPORTED_SPEC_VERSION

    # All methods take key and secret as positional arguments followed by
    # one or more keyword arguments
    async def user_station_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        nmi_code: str = None
    ) -> dict[str, str]:
        """Power station List"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)

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
    ) -> dict[str, str]:
        """Power station details"""

        params: dict[str, Any] = {'id': station_id}
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_data(STATION_DETAIL, key_id, secret, params)

    async def collector_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: int = None,
        nmi_code: str = None
    ) -> dict[str, str]:
        """Datalogger list"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)

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
    ) -> dict[str, str]:
        """Datalogger details"""

        params: dict[str, Any] = {}
        if (collector_sn is not None and collector_id is None):
            params['sn'] = collector_sn
        elif (collector_sn is None and collector_id is not None):
            params['id'] = collector_id
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_COL_ID_OR_SN_ERR)
        return await self._get_data(COLLECTOR_DETAIL, key_id, secret, params)

    async def collector_day(
        self, key_id: str, secret: bytes, /, *,
        collector_sn: int = None,
        time: str,
        time_zone: int,
    ) -> dict[str, str]:
        """Datalogger day statistics"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'time': time,
            'timeZone': time_zone
        }

        if (collector_sn is None):
            raise SoliscloudAPI.SolisCloudError(COL_SN_ERR)
        params['sn'] = collector_sn

        return await self._get_data(COLLECTOR_DAY, key_id, secret, params)

    async def inverter_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None,
        nmi_code: str = None
    ) -> dict[str, str]:
        """Inverter list"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)

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
    ) -> dict[str, str]:
        """Inverter details"""

        params: dict[str, Any] = {}
        if (inverter_sn is not None and inverter_id is None):
            params['sn'] = inverter_sn
        elif (inverter_sn is None and inverter_id is not None):
            params['id'] = inverter_id
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_INV_ID_OR_SN_ERR)
        return await self._get_data(INVERTER_DETAIL, key_id, secret, params)

    async def station_day(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        time: str,
        time_zone: int,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, str]:
        """Station daily graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'money': currency,
            'time': time,
            'timeZone': time_zone
        }

        if (station_id is not None and nmi_code is None):
            params['id'] = station_id
        elif (station_id is None and nmi_code is not None):
            params['nmiCode'] = nmi_code
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_STN_ID_OR_SN_ERR)

        return await self._get_data(STATION_DAY, key_id, secret, params)

    async def station_month(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        month: str,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, str]:
        """Station monthly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'money': currency, 'month': month}

        if (station_id is not None and nmi_code is None):
            params['id'] = station_id
        elif (station_id is None and nmi_code is not None):
            params['nmiCode'] = nmi_code
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_STN_ID_OR_SN_ERR)

        return await self._get_data(STATION_MONTH, key_id, secret, params)

    async def station_year(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        year: str,
        station_id: int = None,
        nmi_code=None
    ) -> dict[str, str]:
        """Station yearly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'money': currency, 'year': year}

        if (station_id is not None and nmi_code is None):
            params['id'] = station_id
        elif (station_id is None and nmi_code is not None):
            params['nmiCode'] = nmi_code
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_STN_ID_OR_SN_ERR)

        return await self._get_data(STATION_YEAR, key_id, secret, params)

    async def station_all(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        station_id: int = None,
        nmi_code: str = None
    ) -> dict[str, str]:
        """Station cumulative graph"""

        params: dict[str, Any] = {'money': currency}
        if (station_id is not None and nmi_code is None):
            params['id'] = station_id
        elif (station_id is None and nmi_code is not None):
            params['nmiCode'] = nmi_code
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_STN_ID_OR_SN_ERR)

        return await self._get_data(STATION_ALL, key_id, secret, params)

    async def inverter_day(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        time: str,
        time_zone: int,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, str]:
        """Inverter daily graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'money': currency,
            'time': time,
            'timeZone': time_zone
        }

        if (inverter_id is not None and inverter_sn is None):
            params['id'] = inverter_id
        elif (inverter_id is None and inverter_sn is not None):
            params['sn'] = inverter_sn
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_INV_ID_OR_SN_ERR)

        return await self._get_data(INVERTER_DAY, key_id, secret, params)

    async def inverter_month(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        month: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, str]:
        """Inverter monthly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'money': currency, 'month': month}

        if (inverter_id is not None and inverter_sn is None):
            params['id'] = inverter_id
        elif (inverter_id is None and inverter_sn is not None):
            params['sn'] = inverter_sn
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_INV_ID_OR_SN_ERR)

        return await self._get_data(INVERTER_MONTH, key_id, secret, params)

    async def inverter_year(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        year: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, str]:
        """Inverter yearly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'money': currency, 'year': year}

        if (inverter_id is not None and inverter_sn is None):
            params['id'] = inverter_id
        elif (inverter_id is None and inverter_sn is not None):
            params['sn'] = inverter_sn
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_INV_ID_OR_SN_ERR)

        return await self._get_data(INVERTER_YEAR, key_id, secret, params)

    async def inverter_all(
        self, key_id: str, secret: bytes, /, *,
        currency: str,
        inverter_id: int = None,
        inverter_sn: str = None
    ) -> dict[str, str]:
        """Inverter cumulative graph"""

        params: dict[str, Any] = {'money': currency}
        if (inverter_id is not None and inverter_sn is None):
            params['id'] = inverter_id
        elif (inverter_id is None and inverter_sn is not None):
            params['sn'] = inverter_sn
        else:
            raise SoliscloudAPI.SolisCloudError(ONLY_INV_ID_OR_SN_ERR)

        return await self._get_data(INVERTER_ALL, key_id, secret, params)

    async def inverter_shelf_time(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        inverter_sn: str = None
    ) -> dict[str, str]:
        """Inverter warranty information"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
        if inverter_sn is None:
            raise SoliscloudAPI.SolisCloudError(INV_SN_ERR)

        params: dict[str, Any] = {
            'pageNo': page_no,
            'pageSize': page_size,
            'sn': inverter_sn}

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
    ) -> dict[str, str]:
        """Alarm check"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)

        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None and device_sn is None:
            params['stationId'] = station_id
        elif station_id is None and device_sn is not None:
            params['alarmDeviceSn'] = device_sn
        else:
            raise SoliscloudAPI.SolisCloudError(
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
    ) -> dict[str, str]:
        """Batch acquire station details"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}

        return await self._get_records(
            STATION_DETAIL_LIST, key_id, secret, params)

    async def inverter_detail_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20
    ) -> dict[str, str]:
        """Batch acquire inverter details"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}

        return await self._get_records(
            INVERTER_DETAIL_LIST, key_id, secret, params)

    async def station_day_energy_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        time: str
    ) -> dict[str, str]:
        """Batch acquire station daily generation"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
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
    ) -> dict[str, str]:
        """Batch acquire station monthly generation"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
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
    ) -> dict[str, str]:
        """Batch acquire station yearly generation"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
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
    ) -> dict[str, str]:
        """EPM list"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)
        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            params['stationId'] = station_id

        return await self._get_records(EPM_LIST, key_id, secret, params)

    async def epm_detail(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str
    ) -> dict[str, str]:
        """EPM details"""

        params: dict[str, Any] = {'sn': epm_sn}

        return await self._get_records(EPM_DETAIL, key_id, secret, params)

    async def epm_day(
        self, key_id: str, secret: bytes, /, *,
        searchinfo: str,
        epm_sn: str,
        time: str,
        time_zone: int
    ) -> dict[str, str]:
        """EPM daily graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.DAY, time)
        params: dict[str, Any] = {
            'searchinfo': searchinfo,
            'sn': epm_sn,
            'time': time,
            'timezone': time_zone}

        return await self._get_records(EPM_DAY, key_id, secret, params)

    async def epm_month(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str,
        month: str,
    ) -> dict[str, str]:
        """EPM monthly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.MONTH, month)
        params: dict[str, Any] = {'sn': epm_sn, 'month': month}

        return await self._get_records(EPM_MONTH, key_id, secret, params)

    async def epm_year(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str,
        year: str
    ) -> dict[str, str]:
        """EPM yearly graph"""

        SoliscloudAPI._verify_date(SoliscloudAPI.DateFormat.YEAR, year)
        params: dict[str, Any] = {'sn': epm_sn, 'year': year}

        return await self._get_records(EPM_YEAR, key_id, secret, params)

    async def epm_all(
        self, key_id: str, secret: bytes, /, *,
        epm_sn: str
    ) -> dict[str, str]:
        """EPM cumulative graph"""

        params: dict[str, Any] = {'sn': epm_sn}

        return await self._get_records(EPM_ALL, key_id, secret, params)

    async def weather_list(
        self, key_id: str, secret: bytes, /, *,
        page_no: int = 1,
        page_size: int = 20,
        station_id: str = None,
        nmi_code: str = None
    ) -> dict[str, str]:
        """Weather list"""

        if page_size > 100:
            raise SoliscloudAPI.SolisCloudError(PAGE_SIZE_ERR)

        params: dict[str, Any] = {'pageNo': page_no, 'pageSize': page_size}
        if station_id is not None:
            # If not specified all inverters for all stations for key_id are
            # returned
            params['stationId'] = station_id
        if nmi_code is not None:
            params['nmiCode'] = nmi_code
        return await self._get_records(WEATHER_LIST, key_id, secret, params)

    async def weather_detail(
        self, key_id: str, secret: bytes, /, *,
        instrument_sn: str = None
    ) -> dict[str, str]:
        """Inverter details"""

        params: dict[str, Any] = {}
        if instrument_sn is None:
            raise SoliscloudAPI.SolisCloudError(WEATHER_SN_ERR)
        params['sn'] = instrument_sn

        return await self._get_data(WEATHER_DETAIL, key_id, secret, params)

    async def _get_records(
        self, canonicalized_resource: str, key_id: str, secret: bytes,
        params: dict[str, Any]
    ):
        """
        Return all records from call
        """

        header: dict[str, str] = SoliscloudAPI._prepare_header(
            key_id, secret, params, canonicalized_resource)

        url = f"{self.domain}{canonicalized_resource}"
        try:
            result = await self._post_data_json(url, header, params)
            return result['page']['records']
        except KeyError as err:
            raise SoliscloudAPI.ApiError("Malformed data", result) from err

    async def _get_data(
        self, canonicalized_resource: str, key_id: str, secret: bytes,
        params: dict[str, Any]
    ):
        """
        Return data from call
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
            raise SoliscloudAPI.SolisCloudError(
                "aiohttp.ClientSession not set")
        try:
            async with async_timeout.timeout(10):
                resp = await SoliscloudAPI._do_post_aiohttp(
                    self._session, url, params, header)

                result = await resp.json()
                if resp.status == HTTPStatus.OK:
                    if result['code'] != '0':
                        raise SoliscloudAPI.ApiError(
                            result['msg'], result['code'])
                    return result['data']
                else:
                    raise SoliscloudAPI.HttpError(resp.status)
        except asyncio.TimeoutError as err:
            if resp is not None:
                await resp.release()
            raise SoliscloudAPI.TimeoutError() from err
        except ClientError as err:
            if resp is not None:
                await resp.release()
            raise SoliscloudAPI.ApiError(err)
        except (KeyError, TypeError) as err:
            raise SoliscloudAPI.ApiError(
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
        err = SoliscloudAPI.SolisCloudError(
            "time must be in format YYYY-MM-DD")
        if format == SoliscloudAPI.DateFormat.MONTH:
            rex = re.compile("^[0-9]{4}-[0-9]{2}$")
            err = SoliscloudAPI.SolisCloudError(
                "month must be in format YYYY-MM")
        elif format == SoliscloudAPI.DateFormat.YEAR:
            rex = re.compile("^[0-9]{4}$")
            err = SoliscloudAPI.SolisCloudError("year must be in format YYYY")
        if not rex.match(date):
            raise err
        return
