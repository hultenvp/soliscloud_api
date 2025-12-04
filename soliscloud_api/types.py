from __future__ import annotations

import re

from abc import ABC, abstractmethod
from enum import IntEnum
from collections import UserDict, UserList
from typing import Any
from datetime import datetime, timezone, timedelta


class EntityType(IntEnum):
    PLANT = 1
    INVERTER = 2
    COLLECTOR = 3


class State(IntEnum):
    ONLINE = 1
    OFFLINE = 2
    ALARM = 3


class InverterOfflineState(IntEnum):
    NORMAL_OFFLINE = 0
    ABNORMAL_OFFLINE = 1


class InverterType(IntEnum):
    GRID = 1
    STORAGE = 2


class InverterModel(IntEnum):
    GRID_TYPE = 1
    GRID_AND_LOAD_SIDE_METER = 2
    GRID_CONNECTED_AND_GRID_SIDE_ELECTRICITY_METER = 3
    ENERGY_STORAGE_AND_LOAD_SIDE_METER = 4
    ENERGY_STORAGE_AND_GRID_SIDE_METER = 5
    RESERVE = 6
    OFF_GRID_ENERGY_STORAGE = 7
    GRID_CONNECTED_ENERGY_STORAGE_DUAL_METER = 8
    AC_COUPLE_WITHOUT_CT = 1001
    AC_COUPLE_WITH_CT = 1002


class PlantType(IntEnum):
    GRID = 0
    ENERGY_STORAGE = 1
    AC_COUPLE = 2
    EPM = 3
    BUILT_IN_METER = 4
    EXTERNAL_METER = 5
    S5_OFFLINE_AND_PARALLEL_STORAGE = 6
    S5_GRID_AND_PARALLEL_STORAGE = 7
    GRID_AND_AC_COUPLE = 8
    OFFGRID_STORAGE = 9
    S6_GRID_AND_PARALLEL_STORAGE = 10
    S6_OFFLINE_AND_PARALLEL_STORAGE = 11


class CollectorState(IntEnum):
    ONLINE = 1
    OFFLINE = 2


class AcOutputType(IntEnum):
    SINGLE_PHASE = 0
    THREE_PHASE = 1


class UnitError(Exception):
    """
    Exception raised for wrong unit assignment.
    """

    def __init__(self, unit, allowed_units):

        self.message = f"{unit} is invalid, allowed: {allowed_units}"
        super().__init__(self.message)


class DimensionedType(UserDict, ABC):
    def __init__(self, value, unit=None):
        super().__init__({'value': float(value), 'unit': unit})
        self._normalize()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __str__(self):
        s = f"{self['value']}"
        if self['unit'] is not None:
            s += f" {self['unit']}"
        return s + f" ({self.__class__.__name__})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value and self.unit == other.unit
        else:
            return False

    def _round_to_int(self):
        if self['value'] == int(self['value']):
            self['value'] = int(self['value'])
        try:
            if self['original_value'] == int(self['original_value']):
                self['original_value'] = int(self['original_value'])
        except KeyError:
            pass

    def original(self):
        d = {}
        try:
            d = {
                'value': self['original_value'],
                'unit': self['original_unit']
            }
        except KeyError:
            d = {'value': self['value'], 'unit': self['unit']}
        return d

    @property
    def original_value(self):
        try:
            return self['original_value']
        except KeyError:
            return self['value']

    @property
    def original_unit(self):
        try:
            return self['original_unit']
        except KeyError:
            return self['unit']

    @property
    def value(self):
        return self['value']

    @property
    def unit(self):
        return self['unit']

    @abstractmethod
    def _normalize(self):
        """ Normalize to default unit """


class GenericType(DimensionedType):
    def __init__(self, value, unit=None):
        super().__init__(value, unit)

    def _normalize(self):
        self._round_to_int()


class SiType(DimensionedType):
    ''' Base class for types expressed in SI units'''
    PREFIXES = ('T', 'G', 'M', 'k', '', 'm', 'µ')
    MULTIPLIERS = {p: 10**(3 * (4 - i)) for i, p in enumerate(PREFIXES)}
    DEFAULT_PREFIX = PREFIXES[4]  # no prefix
    DEFAULT_MULTIPLIER = MULTIPLIERS[DEFAULT_PREFIX]
    BASE_UNIT = None  # to be defined in subclass
    UNITS = ()  # to be defined in subclass

    @classmethod
    def units(cls, base_unit=None):
        return None if base_unit is None else\
            tuple(f"{p}{base_unit}" for p in cls.PREFIXES)

    def __init__(self, value, unit=None):
        if len(self.__class__.UNITS) == 0:
            if self.__class__.BASE_UNIT is None:
                raise AttributeError(
                    "BASE_UNIT not defined in subclass")
            self.__class__.UNITS =\
                tuple(f"{p}{self.__class__.BASE_UNIT}" for p in self.__class__.PREFIXES)   # noqa: E501
        if unit is not None and unit not in self.__class__.UNITS:
            raise UnitError(unit, self.__class__.UNITS)
        super().__init__(value, unit)

    def _normalize(self):
        if self['unit'] is None:
            self['unit'] =\
                self.__class__.DEFAULT_PREFIX + self.__class__.BASE_UNIT
        prefix = self['unit'][:-len(self.__class__.BASE_UNIT)]
        if prefix not in self.__class__.PREFIXES:
            raise UnitError(self['unit'], self.__class__.PREFIXES)
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        self['value'] = self['value'] * (self.__class__.MULTIPLIERS[prefix] / self.__class__.DEFAULT_MULTIPLIER)  # noqa: E501
        self._round_to_int()
        self['unit'] = self.__class__.DEFAULT_PREFIX + self.__class__.BASE_UNIT

    def to_unit(self, unit):
        if unit not in self.__class__.UNITS:
            raise UnitError(unit, self.__class__.UNITS)
        prefix = unit[:-len(self.__class__.BASE_UNIT)]
        value = self['value'] * (self.__class__.DEFAULT_MULTIPLIER / self.__class__.MULTIPLIERS[prefix])  # noqa: E501
        if value == int(value):
            value = int(value)
        return value


class EnergyType(SiType):
    BASE_UNIT = 'Wh'
    DEFAULT_PREFIX = SiType.PREFIXES[3]  # k
    DEFAULT_MULTIPLIER = SiType.MULTIPLIERS[DEFAULT_PREFIX]
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)


class VoltageType(SiType):
    BASE_UNIT = 'V'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)


class CurrentType(SiType):
    BASE_UNIT = 'A'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)


class PowerType(SiType):
    BASE_UNIT = 'W'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()


class ReactivePowerType(SiType):
    BASE_UNIT = 'var'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()


class ApparentPowerType(SiType):
    BASE_UNIT = 'VA'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()


class FrequencyType(SiType):
    BASE_UNIT = 'Hz'
    UNITS = SiType.units(BASE_UNIT)
    DEFAULT = f"{SiType.DEFAULT_PREFIX}{BASE_UNIT}"

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()


class TemperatureType(DimensionedType):
    UNITS = ('℃', 'F', 'K')
    DEFAULT = UNITS[0]
    KELVIN = 273.15

    def __init__(self, value, unit):
        if unit == "C":
            unit = '℃'
        if unit not in TemperatureType.UNITS:
            raise UnitError(unit, TemperatureType.UNITS)
        super().__init__(value, unit)
        self._normalize()

    @property
    def value_celsius(self):
        return self['value']

    @property
    def value_fahrenheit(self):
        return (float(self['value']) * 9 / 5 + 32)

    @property
    def value_kelvin(self):
        return float(self['value'] + self.KELVIN)

    def _normalize(self):
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        v = self['value']
        if self['unit'] != TemperatureType.UNITS[0]:
            if self['unit'] == TemperatureType.UNITS[1]:
                v = float(self['value'] - 32) * 5 / 9
            elif self['unit'] == TemperatureType.UNITS[2]:
                v = float(self['value']) - self.KELVIN

        if self['value'] < -273.15:
            raise ValueError(f"Temperature {self['value']} ℃ below absolute zero")  # noqa: E501
        self['value'] = v
        self._round_to_int()
        self['unit'] = TemperatureType.UNITS[0]


class CurrencyType(DimensionedType):
    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    def _normalize(self):
        pass


class EnumType(UserDict):

    def __init__(self, value: IntEnum):
        if isinstance(value, IntEnum):
            super().__init__(
                {'value': value.value, 'name': value.name.title()})
        else:
            raise TypeError(f"{value} not of type IntEnum")

    def __str__(self):
        s = f"{self['value']}"
        if self['name'] is not None:
            s += f" {self['name']}"
        return s + f" ({self.__class__.__name__})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value and self.name == other.name
        elif isinstance(other, int):
            return self.value == other
        elif isinstance(other, str):
            return self.name == other
        else:
            return False

    @property
    def value(self):
        return self['value']

    @property
    def name(self):
        return self['name']


class ListType(UserList):
    def __init__(self, value):
        if type(value) is list:
            super().__init__(value)
        else:
            raise TypeError(f"{value} not of type list")

    def __str__(self):
        out = '['
        for p in self.data:
            out += '\n'
            r = f"{p}"
            # indent all lines with 2 extra spaces
            r = re.sub(r'(?<=^)(.)', r'  \1', r, flags=re.MULTILINE)
            out += r + ','
        # Remove trailing comma and newline from last element in list
        if out[-1:] == ',':
            out = out[0:-1] + '\n'
        out += ']'
        return out


class DictType(UserDict):
    def __init__(self, value=None):
        if value is None or type(value) is dict:
            super().__init__(value)
        else:
            raise TypeError(f"{value} not of type dict")

    def __str__(self) -> str:
        out = "{"
        for k in self.keys():
            out += '\n'
            r = f"{k}: {self[k]}"
            # indent all lines with 2 extra spaces
            r = re.sub(r'(?<=^)(.)', r'  \1', r, flags=re.MULTILINE)
            out += r + ','
        # Remove trailing comma and newline from last element in list
        if out[-1:] == ',':
            out = out[0:-1] + '\n'
        out += "}"
        return out


class SolisDataFactory:
    """ Convert input dict from API into dict of values
    Keys get normalized to snake_case
    Dimensioned values get parsed, converted and/or normalized
    Unused k/v pairs get dropped
    Values may again be dict or list
    """

    @staticmethod
    def create(type: EntityType, input: dict[str, Any]) -> dict[str, Any]:
        data: DictType = DictType()
        keys = input.keys()
        pattern = re.compile(
            r"""
                (?<!^)      # Not the start of the string
                # alt: (?<!^[a-z]), this would ensure iA,pA,uA etc. do not get
                # underscore, but ia, pa, ua
                (?=[A-Z])   # Followed by an uppercase letter
                |
                (?<=[a-z])  # Preceded by lower case
                (?=[0-9])   # Followed by a digit
                |
                (?<=[0-9])  # Preceded by digit
                (?=[A-Z])   # Followed by uppercase letter
            """, re.VERBOSE)
        nr_of_strings = 0
        try:
            nr_of_strings = input['dcInputtype'] + 1
        except KeyError:
            pass
        for key in keys:
            new_key = pattern.sub('_', key).lower()
            # Fix 'InCome' wrongly converted into 'in_come'
            new_key = re.sub(r'in_come', 'income', new_key)

            if not SolisDataFactory._key_is_unit(key):
                value = input[key]
                unit = None
                if key+'Str' in keys:
                    unit = input[key+'Str']
                elif key+'Unit' in keys:
                    unit = input[key+'Unit']
                elif re.search(r"(?<=(Power|rrent|ltage))(A|B|C|Original)$", key) is not None:  # noqa: E501
                    # Catch backupLookedPowerOriginal, backupLookedPowerA etc.
                    # to use unit from backupLookedPowerStr
                    u_str = re.sub(r"(?<=(Power|rrent|ltage))(A|B|C|Original)$", '', key) + 'Str'  # noqa: E501
                    if u_str in keys:
                        unit = input[u_str]
                elif key.endswith('owerOrigin') or key.endswith('owerOriginV2'):  # noqa: E501
                    if 'powerStr' in keys:
                        unit = input['powerStr']
                elif key.endswith('V2'):
                    # Catch keys ending with V2 to use unit ending with StrV2
                    u_str = key[:-2] + 'StrV2'
                    if u_str in keys:
                        unit = input[u_str]
                    u_str = key[:-2] + 'UnitV2'
                    if u_str in keys:
                        unit = input[u_str]
                elif key.endswith('Origin'):
                    # Catch keys ending with Origin to use unit without Origin
                    u_str = key[:-6] + 'Str'
                    if u_str in keys:
                        unit = input[u_str]
                    u_str = key[:-6] + 'Unit'
                    if u_str in keys:
                        unit = input[u_str]
                elif re.search(r"(Min|Max)$", key) is not None:
                    # Catch keys ending with Min or Max to use unit without
                    # Min/Max
                    u_str = re.sub(r"(Min|Max)$", '', key) + 'Str'
                    if u_str in keys:
                        unit = input[u_str]
                    u_str = re.sub(r"(Min|Max)$", '', key) + 'Unit'
                    if u_str in keys:
                        unit = input[u_str]
                elif key == 'price':
                    if 'money' in keys:
                        unit = input['money']
                    elif 'unit' in keys:
                        unit = input['unit']
                try:
                    if re.search(r"income", new_key, re.IGNORECASE) is not None:  # noqa: E501
                        unit = input['money']
                except KeyError:
                    pass
                try:
                    # Some timestamps are superceded by timezone
                    if new_key[-9:] == 'timestamp':
                        s = re.split(r'/s', value)
                        value = s[0]
                except KeyError:
                    pass
                if new_key[-4:] == 'temp' or new_key[-11:] == 'temperature':
                    try:
                        if unit is None:
                            unit = input['tmpUnit']
                    except KeyError:
                        pass
                d = SolisDataFactory._create_value(
                    type, new_key, value, unit)
                # only create properties for available strings
                if (new_key[0:4] in ['i_pv', 'u_pv', 'pow_', 'mppt']):
                    # find number at end of key string
                    r = re.findall(r'\d+', new_key)
                    # and dropping for string numbers not present
                    if len(r) > 0 and int(r[-1]) > nr_of_strings:
                        d = None
                        # print(f"Dropping: {new_key}")
                if d is not None:
                    data[new_key] = d

        return data

    @staticmethod
    def _key_is_unit(key: str) -> bool:
        is_unit = False
        is_unit |= key[-3:] == 'Str'
        is_unit |= re.search('unit', key, re.IGNORECASE) is not None
        is_unit |= key.endswith('StrV2')
        return is_unit

    @staticmethod
    def _create_value(
        type: EntityType,
        key: str,
        value: Any,
        unit: str = None
    ) -> Any:
        p = None
        if isinstance(value, dict):
            p = SolisDataFactory.create(type, value)
        elif isinstance(value, list):
            p = ListType([
                SolisDataFactory._create_value(type, key, x) for x in value
            ])
        else:
            p = SolisDataFactory._create_typed_value(type, key, value, unit)
        return p

    @staticmethod
    def _create_typed_value(
        type: EntityType,
        key: str,
        value: Any,
        unit: str = None
    ) -> Any:
        p = None
        re_datetime = r'_time$|_timestamp$|_date$'
        re_temperature = r'temperature$|_temp$|tmp_'
        re_apparent_power = r'looked_power$|apparent_power$'
        if unit is not None:
            match(unit):
                case unit if unit in EnergyType.UNITS:
                    p = EnergyType(value, unit)
                case unit if unit in VoltageType.UNITS:
                    p = VoltageType(value, unit)
                case unit if unit in CurrentType.UNITS:
                    p = CurrentType(value, unit)
                case unit if unit in PowerType.UNITS:
                    p = PowerType(value, unit)
                case unit if unit.lower() in ReactivePowerType.UNITS:
                    p = ReactivePowerType(value, unit.lower())
                case unit if unit in ApparentPowerType.UNITS:
                    p = ApparentPowerType(value, unit)
                case unit if unit in FrequencyType.UNITS:
                    p = FrequencyType(value, unit)
                case _ if unit in TemperatureType.UNITS:
                    p = TemperatureType(value, unit)
                case _ if re.search(r"(_income|price)", key, re.IGNORECASE) is not None:  # noqa: E501
                    p = CurrencyType(value, unit)
                case _ if re.search(re_datetime, key, re.IGNORECASE)\
                        is not None:
                    try:
                        regex = '.*UTC([+\-]?)(\d{2}):(\d{2})'  # noqa: W605
                        sign, hours, minutes = re.match(regex, unit).groups()
                        sign = -1 if sign == '-' else 1
                        hours, minutes = int(hours), int(minutes)
                        tz = timezone(sign * timedelta(hours=hours, minutes=minutes))  # noqa: E501
                        p = datetime.fromtimestamp(int(value) / 1e3, tz)
                    except AttributeError:
                        p = datetime.fromtimestamp(int(value) / 1e3)
                case _:
                    p = GenericType(value, unit)
        else:
            match(key):
                case 'state' | 'current_state':
                    p = EnumType(State(int(value)))
                case 'state_exception_flag':
                    p = EnumType(InverterOfflineState(value))
                case 'ac_output_type':
                    p = EnumType(AcOutputType(0 if int(value) == 0 else 1))
                case 'inverter_meter_model':
                    p = EnumType(InverterModel(int(value)))
                case 'station_type':
                    p = EnumType(PlantType(int(value)))
                case 'type':
                    match(type):
                        case EntityType.PLANT:
                            p = EnumType(PlantType(int(value)))
                        case EntityType.INVERTER:
                            p = EnumType(InverterType(int(value)))
                        case _:
                            p = int(value)
                case _ if re.search('pec$|percent$', key, re.IGNORECASE) is not None:  # noqa: E501
                    p = GenericType(int(value)*100, '%')
                case _ if re.search('voltage', key, re.IGNORECASE) is not None:
                    p = VoltageType(value, VoltageType.DEFAULT)
                case _ if re.search('upv', key, re.IGNORECASE) is not None:
                    p = VoltageType(value, VoltageType.DEFAULT)
                case _ if key in ('u_a', 'u_b', 'u_c'):
                    p = VoltageType(value, VoltageType.DEFAULT)
                case _ if re.search('current', key, re.IGNORECASE) is not None:
                    p = CurrentType(value, CurrentType.DEFAULT)
                case _ if re.search('ipv', key, re.IGNORECASE) is not None:
                    p = CurrentType(value, CurrentType.DEFAULT)
                case _ if key in ('i_a', 'i_b', 'i_c'):
                    p = CurrentType(value, CurrentType.DEFAULT)
                case _ if key in ('p_a', 'p_b', 'p_c'):
                    p = PowerType(value, PowerType.DEFAULT)
                case _ if re.search(re_apparent_power, key, re.IGNORECASE)\
                        is not None:
                    p = ApparentPowerType(value, ApparentPowerType.DEFAULT)
                case _ if re.search('reactive_power', key, re.IGNORECASE)\
                        is not None:
                    p = ReactivePowerType(value, ReactivePowerType.DEFAULT)
                case _ if re.search(r"powe{0,1}r{0,1}_?\d{1,2}$", key, re.IGNORECASE) is not None:  # noqa: E501
                    p = PowerType(value, PowerType.DEFAULT)
                case _ if re.search(r"powe{0,1}r{0,1}$", key, re.IGNORECASE)\
                        is not None:
                    p = PowerType(value, PowerType.DEFAULT)
                case _ if re.search(r"energy$", key, re.IGNORECASE)\
                        is not None:
                    p = EnergyType(value, EnergyType.DEFAULT)
                case _ if re.search(r"_time", key) is not None:
                    p = datetime.fromtimestamp(int(value) / 1e3)
                case _ if re.search(r"_date", key) is not None:
                    p = datetime.fromtimestamp(int(value) / 1e3)
                case _ if re.search(re_temperature, key, re.IGNORECASE)\
                        is not None:
                    p = TemperatureType(value, TemperatureType.DEFAULT)
                case _:
                    if unit is not None:
                        p = GenericType(value, unit)
                    else:
                        p = value
        return p
