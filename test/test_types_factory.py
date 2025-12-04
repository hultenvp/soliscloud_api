import json

from soliscloud_api.types import (  # noqa: F401
    EntityType,
    SolisDataFactory,
    GenericType,
    TemperatureType,
    PowerType,
    EnergyType,
    CurrencyType,
    EnumType,
    FrequencyType,
)
from datetime import datetime

mocked_inverter_data_units = {
    "dcInputtype": 2,
    "pow1": 400,
    "pow1Str": "W",
    "pow2": 410,
    "pow2Str": "W",
    "pow3": 420,
    "pow3Str": "W",
    "pow4": 430,
    "pow4Str": "W",
    "YearInCome": 5000,
    "money": "EUR",
    "state": 1,
    "inverterId": 12345,
    "inverterName": "Test Inverter",
    "acOutputPower": 3000,
    "acOutputPowerUnit": "W",
    "data_timestamp": "1687924800000",
    "timezoneStr": "UTC+0",
    "stateExceptionFlag": 0,
    "type": "1",
    "frequency": "50",
    "frequencyStr": "Hz",
    "voltage": "230",
    "voltageStr": "V",
    "current": "10",
    "currentStr": "A",
    "power": "2300",
    "powerStr": "W",
    "energy": "5",
    "energyStr": "kWh",
    "temperature": "45",
    "temperatureStr": "℃",
    "reactivePower": "500",
    "reactivePowerStr": "VAr",
    "apparentPower": "2500",
    "apparentPowerStr": "VA",
    "uA": "400",
    "uAStr": "V",
    "iA": "8",
    "iAStr": "A",
    "pA": "2000",
    "pAStr": "W",
    "powerPec": "1",
    "maxUpv1": "600",
}

mocked_inverter_data_no_units = {
    "dcInputtype": 2,
    "pow1": 400,
    "pow2": 410,
    "pow3": 420,
    "pow4": 430,
    "YearInCome": 5000,
    "money": "EUR",
    "state": 1,
    "inverterId": 12345,
    "inverterName": "Test Inverter",
    "acOutputPower": 3000,
    "data_timestamp": "1687924800000",
    "timezoneStr": "UTC+0",
    "stateExceptionFlag": 0,
    "type": "1",
    "voltage": "230",
    "current": "10",
    "power": "2300",
    "energy": "5",
    "temperature": "45",
    "reactivePower": "500",
    "apparentPower": "2500",
    "uA": "400",
    "iA": "8",
    "pA": "2000",
    "powerPec": "1",
    "maxUpv1": "600",
}

mocked_inverter_nested = {
    "state": 1,
    "inverterId": 12345,
    "inverterName": "Test Inverter",
    "data_timestamp": "1687924800000",
    "timezoneStr": "UTC+0",
    "type": "1",
    "nestedList": [
        {
            "inverterId": 1,
            "inverterName": "Inverter 1",
        },
        {
            "inverterId": 2,
            "inverterName": "Inverter 2",
        },
    ],
    "nestedDict": {
        "frequency": "50",
        "frequencyStr": "Hz",
        "voltage": "230",
        "voltageStr": "V",
    },
}


def test_solis_data_factory_inverter_nested(mocker):
    inverter = SolisDataFactory.create(
        EntityType.INVERTER, mocked_inverter_nested)
    assert inverter["state"].value == 1
    assert inverter["state"].name == "Online"
    assert inverter["inverter_id"] == 12345
    assert inverter["inverter_name"] == "Test Inverter"
    assert inverter["data_timestamp"] == datetime.fromtimestamp(1687924800)
    assert inverter["type"].value == 1
    assert inverter["type"].name == "Grid"
    nested_list = inverter["nested_list"]
    assert nested_list[0]["inverter_id"] == 1
    assert nested_list[0]["inverter_name"] == "Inverter 1"
    assert nested_list[1]["inverter_id"] == 2
    assert nested_list[1]["inverter_name"] == "Inverter 2"
    nested_dict = inverter["nested_dict"]
    assert nested_dict["frequency"].value == 50
    assert nested_dict["frequency"].unit == "Hz"
    assert nested_dict["voltage"].value == 230
    assert nested_dict["voltage"].unit == "V"


# def test_solis_data_factory_station(mocker):
#     inverter = SolisDataFactory.create(
#         EntityType.PLANT, mocked_inverter_nested)
#     assert inverter["data_timestamp"] == datetime.fromtimestamp(1687924800)
#     assert inverter["type"].value == 1
#     assert inverter["type"].name == "Energy_Storage"


def test_solis_data_factory_collector(mocker):
    collector = SolisDataFactory.create(
        EntityType.COLLECTOR, mocked_inverter_nested)
    assert collector["data_timestamp"] == datetime.fromtimestamp(1687924800)
    assert type(collector["type"]) is int
    assert collector["type"] == 1


def test_solis_data_factory_inverter_no_units(mocker):
    inverter = SolisDataFactory.create(
        EntityType.INVERTER, mocked_inverter_data_no_units)
    assert inverter["pow_1"].value == 400
    assert inverter["pow_1"].unit == 'W'
    assert inverter["pow_2"].value == 410
    assert inverter["pow_2"].unit == 'W'
    assert inverter["pow_3"].value == 420
    assert inverter["pow_3"].unit == 'W'
    assert not hasattr(inverter, 'pow4')
    assert inverter["year_income"].value == 5000
    assert inverter["year_income"].unit == "EUR"
    assert inverter["money"] == "EUR"
    assert inverter["state"].value == 1
    assert inverter["state"].name == "Online"
    assert inverter["inverter_id"] == 12345
    assert inverter["inverter_name"] == "Test Inverter"
    assert inverter["ac_output_power"].value == 3000
    assert inverter["ac_output_power"].unit == "W"
    assert inverter["data_timestamp"] == datetime.fromtimestamp(1687924800)
    assert inverter["state_exception_flag"].value == 0
    assert inverter["state_exception_flag"].name == "Normal_Offline"
    assert inverter["type"].value == 1
    assert inverter["type"].name == "Grid"
    assert inverter["voltage"].value == 230
    assert inverter["voltage"].unit == "V"
    assert inverter["current"].value == 10
    assert inverter["current"].unit == "A"
    assert inverter["power"].value == 2300
    assert inverter["power"].unit == "W"
    assert inverter["energy"].value == 5
    assert inverter["energy"].unit == "kWh"
    assert inverter["temperature"].value == 45
    assert inverter["temperature"].unit == "℃"
    assert inverter["reactive_power"].value == 500
    assert inverter["reactive_power"].unit == "var"
    assert inverter["apparent_power"].value == 2500
    assert inverter["apparent_power"].unit == "VA"
    assert inverter["u_a"].value == 400
    assert inverter["u_a"].unit == "V"
    assert inverter["i_a"].value == 8
    assert inverter["i_a"].unit == "A"
    assert inverter["p_a"].value == 2000
    assert inverter["p_a"].unit == "W"
    assert inverter["power_pec"].value == 100
    assert inverter["max_upv_1"].value == 600


def test_solis_data_factory_station(mocker):
    station = None
    with open('test/testdata_station.json', 'r') as f:
        station_data = json.load(f)
        station = SolisDataFactory.create(
            EntityType.PLANT, station_data)
    assert station["id"] == '666666'
    assert station["station_name"] == "TestName"
    assert station["region"].value == 144880
    assert station["region"].unit == "Noord-Brabant"
    assert station["capacity"].value == 1.62
    assert station["capacity"].unit == "kWp"
    assert station["data_timestamp"] == datetime.fromtimestamp(1761467806517/1e3)  # noqa: E501
    assert station["year_energy"].value == 1152
    assert station["year_energy"].unit == "kWh"
    assert station["year_income"].value == 115.21
    assert station["year_income"].unit == "EUR"
    assert station["tmp_min"].value == 8
    assert station["tmp_min"].unit == "℃"
    assert station["price"].value == 0.1
    assert station["price"].unit == "EUR"
    assert station["sys_grid_price_list"][0]["price"].value == 0.1
    assert station["sys_grid_price_list"][0]["price"].unit == "EUR"
    assert isinstance(station["all_income_1"], CurrencyType)
    assert isinstance(station["temp"], TemperatureType)
    assert isinstance(station["tmp_max"], TemperatureType)
    assert isinstance(station["battery_power_origin_v2"], PowerType)
    assert isinstance(station["battery_capacity_energy_origin"], EnergyType)


def test_solis_data_factory_inverter(mocker):
    inverter = None
    with open('test/testdata_inverter.json', 'r') as f:
        inverter_data = json.load(f)
        inverter = SolisDataFactory.create(
            EntityType.INVERTER, inverter_data)
    assert inverter["pow_1"].value == 0
    assert inverter["pow_1"].unit == 'W'
    assert not hasattr(inverter, 'pow2')
    assert isinstance(inverter["current_state"], EnumType)
    assert inverter["year_income"].value == 115.21
    assert inverter["year_income"].unit == "EUR"
    assert inverter["money"] == "EUR"
    assert inverter["state"].value == 1
    assert inverter["state"].name == "Online"
    assert inverter["id"] == '111111'
    assert isinstance(inverter["data_timestamp"], datetime)
    assert inverter["state_exception_flag"].value == 0
    assert inverter["state_exception_flag"].name == "Normal_Offline"
    # TODO: type is missing in real data.
    # assert inverter["type"].value == 1
    # assert inverter["type"].name == "Grid"
    assert isinstance(inverter["fac"], FrequencyType)
    assert inverter["fac"].value == 49.97
    assert inverter["fac"].unit == "Hz"
    assert inverter["u_ac_1"].value == 234.9
    assert inverter["u_ac_1"].unit == "V"
    assert inverter["i_ac_1"].value == 0.3
    assert inverter["i_ac_1"].unit == "A"
    assert inverter["power"].value == 1500
    assert inverter["power"].unit == "W"
    assert inverter["power_pec"].value == 100
