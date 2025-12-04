import pytest
import math
from soliscloud_api.types import (
    GenericType,
    SiType,
    EnergyType,
    VoltageType,
    CurrentType,
    PowerType,
    ReactivePowerType,
    ApparentPowerType,
    FrequencyType,
    TemperatureType,
    CurrencyType,
    EnumType,
    ListType,
    DictType,
    State,
    UnitError
)


@pytest.fixture
def dimensioned_instance():
    instance = GenericType()
    return instance


def test_generic_type_unit_none(mocker):
    gt = GenericType(3)
    assert gt.value == 3
    assert gt.unit is None


def test_generic_type_unit(mocker):
    gt = GenericType(3, 'W')
    assert gt.value == 3
    assert gt.unit == 'W'
    assert f"{gt}" == "3 W (GenericType)"
    assert gt.original() == {'unit': 'W', 'value': 3}


def test_generic_type_original(mocker):
    gt = GenericType(3, 'W')
    assert gt.original_unit == 'W'
    assert gt.original_value == 3


def test_si_type_unit_none(mocker):
    with pytest.raises(AttributeError):
        si = SiType(3)  # noqa: F841


def test_si_type_normalizing(mocker):
    class FakeSiType(SiType):
        BASE_UNIT = 'Fake'

    si = FakeSiType(3, 'Fake')
    assert si.value == 3
    assert si.unit == 'Fake'
    assert f"{si}" == "3 Fake (FakeSiType)"
    assert si.original_unit == 'Fake'
    assert si.original_value == 3
    si = FakeSiType(3, 'kFake')
    assert si.value == 3000
    assert si.unit == 'Fake'
    assert f"{si}" == "3000 Fake (FakeSiType)"
    assert si.original_unit == 'kFake'
    assert si.original_value == 3
    si = FakeSiType(3000, 'mFake')
    assert si.value == 3
    assert si.unit == 'Fake'
    assert f"{si}" == "3 Fake (FakeSiType)"
    assert si.original_unit == 'mFake'
    assert si.original_value == 3000
    si = FakeSiType(1)
    assert si.value == 1
    assert si.unit == 'Fake'
    assert f"{si}" == "1 Fake (FakeSiType)"
    assert si.original_unit == 'Fake'
    assert si.original_value == 1
    with pytest.raises(UnitError):
        si.to_unit('X')
    with pytest.raises(UnitError):
        si = FakeSiType(0.005, 'xFake')


def test_si_type_unit_conversions(mocker):
    class FakeSiType(SiType):
        BASE_UNIT = 'Fake'
    si = FakeSiType(5000, 'mFake')
    assert si.value == 5
    assert si.unit == 'Fake'
    assert f"{si}" == "5 Fake (FakeSiType)"
    assert si.original_unit == 'mFake'
    assert si.original_value == 5000
    assert math.isclose(si.to_unit('GFake'), 0.000000005)
    assert math.isclose(si.to_unit('MFake'), 0.000005)
    assert math.isclose(si.to_unit('kFake'), 0.005)
    assert si.to_unit('Fake') == 5
    assert si.to_unit('mFake') == 5000
    assert si.to_unit('µFake') == 5000000
    assert si.original() == {'unit': 'mFake', 'value': 5000}
    with pytest.raises(UnitError):
        si = FakeSiType(3, 'xFake')  # noqa: F841
    with pytest.raises(UnitError):
        si = FakeSiType(3, 'X')  # noqa: F841


def test_si_type_equality(mocker):
    class FakeSiType(SiType):
        BASE_UNIT = 'Fake'

    class AnotherFakeSiType(SiType):
        BASE_UNIT = 'AnotherFake'
    si1 = FakeSiType(3000, 'mFake')
    si2 = FakeSiType(3, 'Fake')
    si3 = FakeSiType(0.003, 'kFake')
    si4 = FakeSiType(4, 'Fake')
    si5 = AnotherFakeSiType(3, 'AnotherFake')
    assert si1 == si2
    assert si1 == si3
    assert si2 == si3
    assert si1 != si4
    assert si2 != si4
    assert si3 != si4
    assert si1 != si5


def test_energy_type_unit(mocker):
    et = EnergyType(3.5, 'kWh')
    assert et.value == 3.5
    assert et.unit == 'kWh'
    assert f"{et}" == "3.5 kWh (EnergyType)"


def test_voltage_type_unit(mocker):
    et = VoltageType(3.5, 'V')
    assert et.value == 3.5
    assert et.unit == 'V'
    assert f"{et}" == "3.5 V (VoltageType)"


def test_current_type_unit(mocker):
    ct = CurrentType(3.5, 'A')
    assert ct.value == 3.5
    assert ct.unit == 'A'
    assert f"{ct}" == "3.5 A (CurrentType)"


def test_power_type_unit(mocker):
    pt = PowerType(3.5, 'W')
    assert pt.value == 3.5
    assert pt.unit == 'W'
    assert f"{pt}" == "3.5 W (PowerType)"


def test_reactive_power_type_unit(mocker):
    rpt = ReactivePowerType(3.5, 'var')
    assert rpt.value == 3.5
    assert rpt.unit == 'var'
    assert f"{rpt}" == "3.5 var (ReactivePowerType)"


def test_apparent_power_type_unit(mocker):
    apt = ApparentPowerType(3.5, 'VA')
    assert apt.value == 3.5
    assert apt.unit == 'VA'
    assert f"{apt}" == "3.5 VA (ApparentPowerType)"


def test_frequency_type_unit(mocker):
    ft = FrequencyType(3.5, 'Hz')
    assert ft.value == 3.5
    assert ft.unit == 'Hz'
    assert f"{ft}" == "3.5 Hz (FrequencyType)"


def test_temperature_type_unit(mocker):
    tt = TemperatureType(25, 'C')
    assert tt.value == 25
    assert tt.unit == '℃'
    tt = TemperatureType(25, '℃')
    assert tt.value == 25
    assert tt.unit == '℃'
    assert f"{tt}" == "25 ℃ (TemperatureType)"
    assert math.isclose(tt.value_kelvin, 298.15)
    tt = TemperatureType(77, 'F')
    assert math.isclose(tt.value, 25)
    assert tt.unit == '℃'
    assert f"{tt}" == "25 ℃ (TemperatureType)"
    assert math.isclose(tt.value_kelvin, 298.15)
    tt = TemperatureType(298.15, 'K')
    assert math.isclose(tt.value, 25)
    assert tt.unit == '℃'
    assert f"{tt}" == "25 ℃ (TemperatureType)"
    assert math.isclose(tt.value_kelvin, 298.15)
    assert math.isclose(tt.value_fahrenheit, 77)
    assert math.isclose(tt.value_celsius, 25)
    with pytest.raises(ValueError):
        tt = TemperatureType(-300, '℃')  # noqa: F841
    with pytest.raises(ValueError):
        tt = TemperatureType(-10, 'K')  # noqa: F841
    with pytest.raises(ValueError):
        tt = TemperatureType(-500, 'F')  # noqa: F841
    with pytest.raises(UnitError):
        tt = TemperatureType(25, 'X')  # noqa: F841


def test_currency_type_unit(mocker):
    ct = CurrencyType(3.5, 'EUR')
    assert ct.value == 3.5
    assert ct.unit == 'EUR'
    assert f"{ct}" == "3.5 EUR (CurrencyType)"


def test_enum_type(mocker):
    et = EnumType(State(State.ONLINE))
    assert et.value == State.ONLINE
    assert f"{et}" == "1 Online (EnumType)"
    et = EnumType(State(State.OFFLINE))
    assert et.value == State.OFFLINE
    assert f"{et}" == "2 Offline (EnumType)"
    with pytest.raises(TypeError):
        et = EnumType(3)  # noqa: F841
    with pytest.raises(TypeError):
        et = EnumType("ONLINE")  # noqa: F841


def test_enum_type_equality(mocker):
    et1 = EnumType(State(State.ONLINE))
    et2 = EnumType(State(State.ONLINE))
    et3 = EnumType(State(State.OFFLINE))
    et4 = State(State.ONLINE)
    et5 = 1
    et6 = "Online"
    assert et1 == et2
    assert et1 != et3
    assert et2 != et3
    assert et1 == et4
    assert et3 != et4
    assert et1 == et5
    assert et1 == et6
    assert et1 != 0.003


def test_list_type(mocker):
    lt = ListType([1, 2, 3])
    assert lt.data == [1, 2, 3]
    assert f"{lt}" == "[\n  1,\n  2,\n  3\n]"
    lt = ListType([EnergyType(1, 'kWh'), EnergyType(2000, 'Wh')])
    assert isinstance(lt.data[0], EnergyType)
    assert isinstance(lt.data[1], EnergyType)
    assert lt.data[0].value == 1
    assert lt.data[1].value == 2
    assert f"{lt}" == "[\n  1 kWh (EnergyType),\n  2 kWh (EnergyType)\n]"
    with pytest.raises(TypeError):
        lt = ListType(3)  # noqa: F841


def test_dict_type(mocker):
    dt = DictType({'a': 1, 'b': 2})
    assert dt.data == {'a': 1, 'b': 2}
    assert f"{dt}" == "{\n  a: 1,\n  b: 2\n}"
    lt = ListType([EnergyType(1, 'kWh'), EnergyType(2000, 'Wh')])
    dt = DictType({'energy_values': lt, 'status': EnumType(State(State.ONLINE))})  # noqa: E501
    assert isinstance(dt.data['energy_values'], ListType)
    assert isinstance(dt.data['status'], EnumType)
    assert dt.data['energy_values'].data[0].value == 1
    assert dt.data['energy_values'].data[1].value == 2
    assert dt.data['status'].value == State.ONLINE
    assert f"{dt}" == "{\n  energy_values: [\n    1 kWh (EnergyType),\n    2 kWh (EnergyType)\n  ],\n  status: 1 Online (EnumType)\n}"  # noqa: E501
    with pytest.raises(TypeError):
        dt = DictType(3)  # noqa: F841
