import pytest
import json
from soliscloud_api import Plant, Inverter, Collector
from .const import (
    KEY,
    SECRET,
)


def validate_plant(plant: Plant, station_data: dict):
    assert plant.plant_id == station_data['id']
    assert plant.data_timestamp == int(station_data['dataTimestamp'])/1e3
    # Some random fields that have to be parsed correctly
    assert plant.data["station_name"] == "TestName"
    assert plant.data["year_energy"].value == 1152
    assert plant.data["year_energy"].unit == "kWh"


def validate_inverter(inverter: Inverter, inverter_data: dict):
    assert inverter.inverter_id == inverter_data['id']
    assert inverter.data_timestamp == int(inverter_data['dataTimestamp'])/1e3
    assert inverter.data["state"].value == 1
    assert inverter.data["state"].name == "Online"
    assert inverter.data["power"].value == 1500
    assert inverter.data["power"].unit == "W"


def validate_collector(collector: Collector, collector_data: dict):
    assert collector.collector_id == collector_data['id']
    assert collector.data_timestamp == int(collector_data['dataTimestamp'])/1e3
    assert collector.data["model"] == "WIFI"


def test_plant_creation_from_data(mocker):
    with open('test/testdata_station.json', 'r') as f:
        station_data = json.load(f)
        station_data2 = station_data.copy()
        # first test filtering by wrong plant ID
        plants = Plant.from_data(station_data, plant_id=0)
        assert len(plants) == 0
        # test with single station data
        plants = Plant.from_data(station_data)
        validate_plant(plants[0], station_data)
        # test with two identical stations in a list
        station_data_list = [station_data, station_data2]
        plants = Plant.from_data(station_data_list)
        validate_plant(plants[0], station_data)
        validate_plant(plants[1], station_data2)
        assert plants[0] == plants[1]
        # test string representation
        assert str(plants[0]) == str(plants[1])
        # test with two different stations in a list
        station_data2['id'] = '1010101010'
        station_data_list = [station_data, station_data2]
        plants = Plant.from_data(station_data_list)
        validate_plant(plants[0], station_data)
        validate_plant(plants[1], station_data2)
        assert plants[0] != plants[1]
        # test string representation
        assert str(plants[0]) != str(plants[1])


def test_plant_constructor():
    with open('test/testdata_station.json', 'r') as f:
        station_data = json.load(f)
        plant = Plant(station_data)
        validate_plant(plant, station_data)
        # test with missing required id field
        station_data.pop('id')
        with pytest.raises(ValueError):
            _ = Plant(station_data)
        # test with invalid data type
        with pytest.raises(ValueError):
            _ = Plant(list(station_data))


def test_fail_plant_creation_from_data():
    with open('test/testdata_station.json', 'r') as f:
        station_data = json.load(f)
        station_data.pop('id')
        # test with missing required id field
        with pytest.raises(ValueError):
            _ = Plant.from_data(station_data)
        # test with invalid data type
        station_data = list(station_data)
        with pytest.raises(ValueError):
            _ = Plant.from_data(station_data)


def test_plant_creation_from_data_with_inverters():
    with open('test/testdata_station.json', 'r') as f, \
            open('test/testdata_inverter.json', 'r') as g:
        station_data = json.load(f)
        inverter_data = json.load(g)
        inverter_data2 = inverter_data.copy()
        inverter_data2['id'] = '1010101010'
        # test with adding multiple inverters to a plant in one go
        plants = Plant.from_data(station_data)
        inverter_data_list = [inverter_data]
        inverter_data_list.append(inverter_data2)
        inverters = Inverter.from_data(inverter_data_list)
        plants[0].add_inverters(inverters)
        validate_inverter(plants[0].inverters[0], inverter_data)
        validate_inverter(plants[0].inverters[1], inverter_data2)
        assert plants[0].inverters[0] != plants[0].inverters[1]
        # test with adding inverters one by one
        plants = Plant.from_data(station_data)
        inverter_data_list = [inverter_data]
        inverter_data_list.append(inverter_data2)
        inverters = Inverter.from_data(inverter_data_list)
        plants[0].add_inverter(inverters[0])
        plants[0].add_inverter(inverters[1])
        validate_inverter(plants[0].inverters[0], inverter_data)
        validate_inverter(plants[0].inverters[1], inverter_data2)
        assert plants[0].inverters[0] != plants[0].inverters[1]
        # test inequality with invalid type
        assert plants[0].inverters[0] != 3
        # remove timestamp from plant data and test None
        plants[0]._data.pop('data_timestamp')
        assert plants[0].data_timestamp is None
        # remove id and test attribute error
        plants[0]._data.pop('id')
        with pytest.raises(AttributeError):
            _ = plants[0].plant_id


def test_inverter_constructor():
    with open('test/testdata_inverter.json', 'r') as f:
        inverter_data = json.load(f)
        inverter = Inverter(inverter_data)
        validate_inverter(inverter, inverter_data)
        # test attribute error for missing id
        inverter.data.pop('id')
        with pytest.raises(AttributeError):
            _ = inverter.inverter_id
        # test with missing required id field
        inverter_data.pop('id')
        with pytest.raises(ValueError):
            _ = Inverter(inverter_data)
        # test with invalid data type
        with pytest.raises(ValueError):
            _ = Inverter(list(inverter_data))


def test_inverter_creation_from_data():
    with open('test/testdata_inverter.json', 'r') as f:
        inverter_data = json.load(f)
        inverter_data2 = inverter_data.copy()
        inverters = Inverter.from_data(inverter_data)
        validate_inverter(inverters[0], inverter_data)
        # test with two identical inverters in a list
        inverter_data_list = [inverter_data, inverter_data2]
        inverters = Inverter.from_data(inverter_data_list)
        validate_inverter(inverters[0], inverter_data)
        validate_inverter(inverters[1], inverter_data2)
        assert inverters[0] == inverters[1]
        # test string representation
        assert str(inverters[0]) == str(inverters[1])
        # test with two different inverters in a list
        inverter_data2['id'] = '1010101010'
        inverter_data_list = [inverter_data, inverter_data2]
        inverters = Inverter.from_data(inverter_data_list)
        validate_inverter(inverters[0], inverter_data)
        validate_inverter(inverters[1], inverter_data2)
        assert inverters[0] != inverters[1]
        # test string representation
        assert str(inverters[0]) != str(inverters[1])


def test_inverter_creation_from_data_with_collectors():
    with open('test/testdata_inverter.json', 'r') as f, \
            open('test/testdata_collector.json', 'r') as g:
        inverter_data = json.load(f)
        collector_data = json.load(g)
        collector_data2 = collector_data.copy()
        collector_data2['id'] = '1010101010'
        collector_data_list = [collector_data, collector_data2]
        collectors = Collector.from_data(collector_data_list)
        # test with adding multiple collectors to an inverter in one go
        inverters = Inverter.from_data(inverter_data)
        inverter = inverters[0]
        inverter.add_collectors(collectors)
        validate_collector(inverter.collectors[0], collector_data)
        validate_collector(inverter.collectors[1], collector_data2)
        assert inverter.collectors[0] != inverter.collectors[1]
        # test with adding collectors one by one
        inverters = Inverter.from_data(inverter_data)
        inverter2 = inverters[0]
        inverter2.add_collector(collectors[0])
        inverter2.add_collector(collectors[1])
        validate_collector(inverter2.collectors[0], collector_data)
        validate_collector(inverter2.collectors[1], collector_data2)
        assert inverter2.collectors[0] != inverter2.collectors[1]
        assert inverter == inverter2
        assert str(inverter) == str(inverter2)


def test_collector_constructor():
    with open('test/testdata_collector.json', 'r') as f:
        collector_data = json.load(f)
        collector = Collector(collector_data)
        validate_collector(collector, collector_data)
        collector2 = Collector(collector_data)
        assert collector == collector2
        assert str(collector) == str(collector2)
        # test with missing required id field
        collector_data.pop('id')
        with pytest.raises(ValueError):
            _ = Collector(collector_data)
        # test with invalid data type
        with pytest.raises(ValueError):
            _ = Collector(list(collector_data))
        # collector id attribute error
        collector.data.pop('id')
        with pytest.raises(AttributeError):
            _ = collector.collector_id


@pytest.mark.asyncio
async def test_plant_creation_from_session(mocker):
    with open('test/testdata_station.json', 'r') as f, \
            open('test/testdata_inverter.json', 'r') as g, \
            open('test/testdata_collector.json', 'r') as h:
        station_data = json.load(f)
        inverter_data = json.load(g)
        collector_data = json.load(h)
        session = 1234567890
        mocker.patch('soliscloud_api.client.SoliscloudAPI.station_detail', return_value=station_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.station_detail_list', return_value=[station_data])  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.inverter_detail', return_value=inverter_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.inverter_detail_list', return_value=[inverter_data])  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_detail', return_value=collector_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_list',  return_value=[collector_data])  # noqa: E501
        # First test without specifying station ID
        plants = await Plant.from_session(session, KEY, SECRET)  # noqa: E501
        validate_plant(plants[0], station_data)
        inverter = plants[0].inverters[0]
        validate_inverter(inverter, inverter_data)
        collector = inverter.collectors[0]
        validate_collector(collector, collector_data)
        # Now test with specifying station ID
        plants = await Plant.from_session(session, KEY, SECRET, station_data['id'])  # noqa: E501
        validate_plant(plants[0], station_data)
        inverter = plants[0].inverters[0]
        validate_inverter(inverter, inverter_data)
        collector = inverter.collectors[0]
        validate_collector(collector, collector_data)


@pytest.mark.asyncio
async def test_inverter_creation_from_session(mocker):
    with open('test/testdata_station.json', 'r') as f, \
            open('test/testdata_inverter.json', 'r') as g, \
            open('test/testdata_collector.json', 'r') as h:
        station_data = json.load(f)
        inverter_data = json.load(g)
        collector_data = json.load(h)
        session = 1234567890
        mocker.patch('soliscloud_api.client.SoliscloudAPI.inverter_detail', return_value=inverter_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.inverter_detail_list', return_value=[inverter_data])  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_detail', return_value=collector_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_list',  return_value=[collector_data])  # noqa: E501
        # Test inverter without specifying plant ID
        inverters = await Inverter.from_session(session, KEY, SECRET)  # noqa: E501
        inverter = inverters[0]
        validate_inverter(inverter, inverter_data)
        collector = inverter.collectors[0]
        validate_collector(collector, collector_data)
        # Test inverter with specifying plant ID
        inverters = await Inverter.from_session(session, KEY, SECRET, plant_id=station_data['id'])  # noqa: E501
        inverter = inverters[0]
        inverter = inverters[0]
        validate_inverter(inverter, inverter_data)
        collector = inverter.collectors[0]
        validate_collector(collector, collector_data)
        # Test inverter with specifying inverter ID
        inverters = await Inverter.from_session(session, KEY, SECRET, inverter_id=inverter_data['id'])  # noqa: E501
        inverter = inverters[0]
        inverter = inverters[0]
        validate_inverter(inverter, inverter_data)
        collector = inverter.collectors[0]
        validate_collector(collector, collector_data)


@pytest.mark.asyncio
async def test_collector_creation_from_session(mocker):
    with open('test/testdata_station.json', 'r') as f, \
            open('test/testdata_collector.json', 'r') as h:
        station_data = json.load(f)
        collector_data = json.load(h)
        session = 1234567890
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_detail', return_value=collector_data)  # noqa: E501
        mocker.patch('soliscloud_api.client.SoliscloudAPI.collector_list',  return_value=[collector_data])  # noqa: E501
        # Test collector without specifying plant ID
        collectors = await Collector.from_session(session, KEY, SECRET)  # noqa: E501
        collector = collectors[0]
        validate_collector(collector, collector_data)
        # Test collector with specifying plant ID
        collectors = await Collector.from_session(session, KEY, SECRET, plant_id=station_data['id'])  # noqa: E501
        collector = collectors[0]
        validate_collector(collector, collector_data)
        # Test collector with specifying collector ID
        collectors = await Collector.from_session(session, KEY, SECRET, collector_id=collector_data['id'])  # noqa: E501
        collector = collectors[0]
        validate_collector(collector, collector_data)
        # test collector with specifying collector SN
        collectors = await Collector.from_session(session, KEY, SECRET, collector_sn=collector_data['sn'])  # noqa: E501
        collector = collectors[0]
        validate_collector(collector, collector_data)
