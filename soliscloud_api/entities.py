from __future__ import annotations

from typing import Any
from datetime import datetime
from aiohttp import ClientSession

from soliscloud_api import SoliscloudAPI, SoliscloudError
from soliscloud_api.types import EntityType, SolisDataFactory

WHITELIST = (
    'a',
    'b',
    'c'
)


def _normalize_to_list(data):
    """Ensure input is always a list of dicts."""
    if isinstance(data, dict):
        return [data]
    return data


class SolisEntity(object):
    """Base class with common methods for SolisCloud entities."""
    def __init__(
        self,
        type: EntityType,
        data: dict[str, Any] = None,
        whitelist: list[str] = None
    ):
        """Base class constructor. This is not meant to be called and there
        are no checks on data passed. Use from_data() or from_session()
        class methods on derived classes instead.

        Args:
            type (EntityType): Type of entity (e.g., EntityType.PLANT)
            data (dict[str, Any], optional): Data for this entity as received
                from Soliscloud API call. Defaults to None.
            whitelist (list[str], optional): Not yet used, ignore.
                Defaults to None.
        """
        self._data = None
        if data is not None:
            self._data = SolisDataFactory.create(type, data)
        self._whitelist = whitelist

    def __str__(self) -> str:
        out = f"timestamp data: {self.data_timestamp}"
        return out

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data == other._data
        return NotImplemented

    @property
    def data(self) -> dict:
        return self._data

    @property
    def data_timestamp(self) -> datetime:
        if self._data is None or 'data_timestamp' not in self._data:
            return None
        return self._data['data_timestamp'].timestamp()

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any] | list[dict[str, Any]],
        /, **filters
    ) -> list["SolisEntity"]:
        """
        Generic method to parse data and return entity objects.
        Filters can be passed as keyword arguments (e.g., plantId=..., id=...).
        Args:
            data (dict[str, Any] | list[dict[str, Any]]):
                response from Soliscloud API call.
            **filters: key-value pairs to filter records.
        Returns:
            list[SolisEntity]: list of zero or more entity objects.
        """
        return cls._do_initialize_from_data(data, **filters)

    @classmethod
    def _do_initialize_from_data(
        cls,
        data: dict[str, Any] | list[dict[str, Any]],
        /, **filters
    ) -> list["SolisEntity"]:

        items = []
        data_list = _normalize_to_list(data)
        for record in data_list:
            if not isinstance(record, dict):
                raise ValueError(f"Each {cls.__name__} record must be a dict")
            if 'id' not in record:
                raise ValueError(f"{cls.__name__} record missing 'id'")
            match = True
            for key, value in filters.items():
                # Map filter keys to record keys if needed
                if value is not None and record.get(key) != value:
                    match = False
                    break
            if match:
                items.append(cls(record))
        return items


class Collector(SolisEntity):
    def __init__(self, data: dict[str, Any]) -> None:
        """Constructor. Do not use directly. Use from_data or from_session

        Args:
            data (dict[str, Any]): Data from API response belonging to entity.

        Raises:
            ValueError: Raised when data does not pass minimal conditions.
        """
        if not isinstance(data, dict):
            raise ValueError("Collector data must be a dict")
        if 'id' not in data:
            raise ValueError("Collector data must include 'id'")
        super().__init__(EntityType.COLLECTOR, data)

    def __str__(self):
        out = f"collector id: {self._data['id']}\n"
        return out

    @property
    def collector_id(self):
        '''Alias for 'id' attribute '''
        try:
            return self._data['id']
        except KeyError:
            raise AttributeError("Collector data has no 'id' attribute")

    @classmethod
    async def from_session(
        cls,
        session: ClientSession,
        key_id: str,
        secret: bytes,
        /, *,
        plant_id: int = None,
        nmi_code: str = None,
        collector_sn: str = None,
        collector_id: int = None
    ) -> list[Collector]:
        """Uses SolisCloudAPI to create Collector objects
        Will return objects for all collectors under account if plant_id
        is specified
        Will return a list containing the Collector object(s) for collector_id
        or collector_sn if specified.
        First evaluates plant_id, then collector_id, then collector_sn.

        Args:
            session (ClientSession): http session to use
            key_id (str): API key
            secret (bytes): API secret
            plant_id (int, optional): Plant ID to filter collectors by.
                Defaults to None.
            nmi_code (str, optional): NMI code to filter by. Only used
                in AUS. Defaults to None.
            collector_sn (str, optional): collector serial number to filter by.
                Defaults to None.
            collector_id (int, optional): collector ID to filter by.
                Defaults to None.

        Returns:
            list[Collector]: Returns a list of zero or more Collector objects
        """
        collectors: list[Collector] = []
        try:
            soliscloud = SoliscloudAPI(
                SoliscloudAPI.DEFAULT_DOMAIN, session)
            collector_data = []
            if plant_id is not None:
                collector_data = await soliscloud.collector_list(
                    key_id, secret,
                    station_id=plant_id,
                    nmi_code=nmi_code)
            elif collector_id is not None:
                collector_data.append(await soliscloud.collector_detail(
                    key_id, secret,
                    collector_id=collector_id))
            elif collector_sn is not None:
                collector_data.append(await soliscloud.collector_detail(
                    key_id, secret,
                    collector_sn=collector_sn))
            else:
                collector_data = await soliscloud.collector_list(
                    key_id, secret)
            for record in collector_data:
                if plant_id is None or record['stationId'] == plant_id:
                    collector = cls(record)
                    collectors.append(collector)
        except SoliscloudError:
            pass
        return collectors

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any] | list[dict[str, Any]],
        /, *,
        collector_id: str = None,
        station_id: str = None
    ) -> list[Collector]:
        """Parse data retrieved from collector_detail or collector_list
        and return Collector objects.
        collector_id can be used to filter.

        Args:
            data (dict[str, Any] | list[dict[str, Any]]):
                response from collector_detail() or collector_list() call.
            collector_id (str, optional): Only collectors for matching
                collector_id will be created. Defaults to None.
            station_id (str, optional): Only collectors for matching
                station_id will be created.
                Defaults to None.

        Returns:
            list[Collector]: list of zero or more Collector objects
        """
        return cls._do_initialize_from_data(
            data, id=collector_id, stationId=station_id)


class Inverter(SolisEntity):
    def __init__(self, data: dict[str, Any]) -> None:
        """Constructor. Do not use directly. Use from_data or from_session

        Args:
            data (dict[str, Any]): Data from API response belonging to entity.

        Raises:
            ValueError: Raised when data does not pass minimal conditions.
        """
        if not isinstance(data, dict):
            raise ValueError("Inverter data must be a dict")
        if 'id' not in data:
            raise ValueError("Inverter data must include 'id'")
        super().__init__(EntityType.INVERTER, data)
        self._collectors = list()

    def add_collectors(self, collectors: list[Collector]) -> None:
        """Register list of collectors under inverter

        Args:
            collectors (list[Collector]): List of collector entities to
                register
        """
        self._collectors = collectors

    def add_collector(self, collector: Collector) -> None:
        """Add collector entity to list of registered collectors

        Args:
            collector (Collector): Collector entity to add
        """
        self._collectors.append(collector)

    def __str__(self):
        out = f"inverter id: {self._data['id']}, collector id's: ["
        for collector in self._collectors:
            out += f"{collector.collector_id}, "
        if len(self._collectors) > 0:
            out = out[:-2]
        out += "]"
        return out

    @property
    def inverter_id(self):
        '''Alias for 'id' attribute '''
        try:
            return self._data['id']
        except KeyError:
            raise AttributeError("Inverter data has no 'id' attribute")

    @property
    def collectors(self) -> list[Collector]:
        """Return list of collectors registered under inverter

        Returns:
            list[Collector]: List of Collector objects
        """
        return self._collectors

    @classmethod
    async def from_session(
        cls,
        session: ClientSession,
        key_id: str,
        secret: bytes,
        /, *,
        plant_id: int = None,
        inverter_id: int = None
    ) -> list[Inverter]:
        """Uses SolisCloudAPI to create Inverter objects
        Works recursive and will also create underlying Collector objects.
        plant_id and inverter_id can be used to filter.
        Will return objects for all inverters under account if no plant_id
        or inverter_id is specified

        Args:
            session (ClientSession): http session to use
            key_id (str): API key
            secret (bytes): API secret
            plant_id (int, optional):
                Only inverters for matching plant_id will be created.
                Defaults to None.
            inverter_id (int, optional):
                Only inverters for matching inverter_id will be created.
                Defaults to None.

        Returns:
            list[Inverter]: list of zero or more Inverter objects
        """
        inverters: list[Inverter] = []
        try:
            soliscloud = SoliscloudAPI(
                SoliscloudAPI.DEFAULT_DOMAIN, session)
            inverter_data = []
            if inverter_id is not None:
                inverter_data.append(await soliscloud.inverter_detail(
                    key_id, secret,
                    inverter_id=inverter_id))
            else:
                inverter_data = await soliscloud.inverter_detail_list(
                    key_id, secret)
            for record in inverter_data:
                if inverter_id is None or record['id'] == inverter_id:
                    if plant_id is None or record['stationId'] == plant_id:
                        inverter = cls(record)
                        collectors = await Collector.from_session(
                            session, key_id, secret,
                            collector_id=inverter.data["collector_id"])
                        inverter._collectors = collectors
                        inverters.append(inverter)
        except SoliscloudError:
            pass
        return inverters

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any] | list[dict[str, Any]],
        /, *,
        plant_id: int = None,
        inverter_id: int = None,
        id: int = None
    ) -> list[Inverter]:
        """Parse data retrieved from inverter_detail or inverter_detail_list
        and return Inverter objects.
        plant_id and inverter_id can be used to filter.

        Args:
            data (dict[str, Any] | list[dict[str, Any]]):
                response from inverter_detail() or inverter_detail_list() call.
            plant_id (int, optional):
                Only inverters for matching plant_id will be created.
                Defaults to None.
            inverter_id (int, optional):
                Only inverters for matching inverter_id will be created.
                Defaults to None.
        Returns:
            list[Inverter]: list of zero or more Inverter objects
        """
        return cls._do_initialize_from_data(
            data, stationId=plant_id, id=inverter_id)


class Plant(SolisEntity):
    def __init__(self, data: dict[str, Any]) -> None:
        """Constructor. Do not use directly. Use from_data or from_session

        Args:
            data (dict[str, Any]): Data from API response belonging to entity.

        Raises:
            ValueError: Raised when data does not pass minimal conditions.
        """
        if not isinstance(data, dict):
            raise ValueError("Plant data must be a dict")
        if 'id' not in data:
            raise ValueError("Plant data must include 'id'")
        super().__init__(EntityType.PLANT, data)
        self._inverters: list[Inverter] = []

    def __str__(self):
        out = f"plant id: {self.plant_id}\n"
        out += super().__str__()
        out += "\ninverters: [\n"
        for i in self.inverters:
            out += "  " + str(i) + ",\n"
        if out[-2:] == ",\n":
            out = out[:-2] + "\n]"
        elif out[-2:] == "[\n":
            out = out[:-1] + "]"
        return out

    def add_inverters(self, inverters: list[Inverter]) -> None:
        """Register list of inverters under plant

        Args:
            inverters (list[Inverter]): List of inverter entities to register
        """
        self._inverters = inverters

    def add_inverter(self, inverter: Inverter) -> None:
        """Add inverter entity to list of registered inverters

        Args:
            inverter (Inverter): Inverter entity to add
        """
        self._inverters.append(inverter)

    @property
    def plant_id(self):
        '''Alias for 'id' attribute '''
        try:
            return self._data['id']
        except KeyError:
            raise AttributeError("Plant data has no 'id' attribute")

    @property
    def inverters(self) -> list[Inverter]:
        return self._inverters

    @classmethod
    async def from_session(
        cls,
        session: ClientSession,
        key_id: str, secret: bytes,
        plant_id: int = None
    ) -> list[Plant]:
        """Uses SoliscloudAPI to create Plant objects
        Works recursive and will also create underlying Inverter objects and
        their Collector objects, building a whole object tree.
        If no plant_id is specified then Plant objects will be created for all
        plants under account.

        Args:
            session (ClientSession): http session to use
            key_id (str): API key
            secret (bytes): API secret
            plant_id (int, optional): plant ID to get data from.
            Defaults to None.

        Returns:
            list[Plant]: list of zero or more Plant objects
        """

        plants: list[Plant] = []
        try:
            plants: list[Plant] = []
            plant_data: list[dict[str, Any]] = []
            soliscloud = SoliscloudAPI(
                SoliscloudAPI.DEFAULT_DOMAIN, session)
            if plant_id is None:
                plant_data = await soliscloud.station_detail_list(
                    key_id, secret)
            else:
                plant_data = [await soliscloud.station_detail(
                    key_id, secret,
                    station_id=plant_id)]

            for plant_record in plant_data:
                plant = cls(plant_record)
                plant.add_inverters(await Inverter.from_session(
                    session, key_id, secret,
                    plant_id=plant.plant_id))

                plants.append(plant)
        except SoliscloudError:
            pass
        return plants

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any] | list[dict[str, Any]],
        /, *,
        plant_id: int = None
    ) -> list[Plant]:
        """Parse data retrieved from stationDetail or stationDetailList and
        return Plant objects

        Args:
            data (dict[str, Any] | list[dict[str, Any]]):
                response from station_detail_list() or station_detail() call
            plant_id (int, optional): plant id to use.
                Defaults to None. If not given a plant is created for all
                records in the input data

        Returns:
            list[Plant]: A list of zero or more Plant objects
        """
        return cls._do_initialize_from_data(data, id=plant_id)
