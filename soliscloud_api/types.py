from __future__ import annotations

import re

from abc import ABC, abstractmethod
from enum import IntEnum
from collections import UserDict, UserList
from typing import Any
from datetime import datetime, tzinfo, timezone, timedelta


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


class UnitError(Exception):
    """
    Exception raised for wrong unit assignment.
    """

    def __init__(self, unit, allowed_units):

        self.message = f"{unit} is invalid, allowed: {allowed_units}"
        super().__init__(self.message)


class DimensionedType(UserDict, ABC):

    def __init__(self, value, unit=None):
        try:
            if unit not in self.__class__.UNITS:
                raise UnitError(unit, self.__class__.UNITS)
        except AttributeError:
            pass
        super().__init__({'value': value, 'unit': unit})

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

    def original(self):
        d = {}
        try:
            d = {
                'value': self['original_value'],
                'unit': self['original_unit']
            }
        except AttributeError:
            d = {'value': self['value'], 'unit': self['unit']}
        return d

    @property
    def original_value(self):
        try:
            return self['original_value']
        except AttributeError:
            return self['value']

    @property
    def original_unit(self):
        try:
            return self['original_unit']
        except AttributeError:
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
    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    def _normalize(self):
        pass


class EnergyType(DimensionedType):
    UNITS = ('Wh', 'kWh', 'MWh')
    DEFAULT = UNITS[1]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    @property
    def value_mwh(self):
        return self['value']/1000

    @property
    def value_wh(self):
        return self['value']*1000

    def _normalize(self):
        if self['unit'] == EnergyType.UNITS[1]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == EnergyType.UNITS[0]:
            self['value'] = self['value']/1000
        elif self['unit'] == EnergyType.UNITS[2]:
            self['value'] = self['value']*1000
        else:
            pass
        self['unit'] = EnergyType.UNITS[1]


class VoltageType(DimensionedType):
    UNITS = ('V', 'kV')
    DEFAULT = UNITS[0]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    @property
    def value_kv(self):
        return self['value']/1000

    def _normalize(self):
        if self['unit'] == VoltageType.UNITS[0]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == VoltageType.UNITS[1]:
            self['value'] = self['value']*1000
        else:
            pass
        self['unit'] = VoltageType.UNITS[0]


class CurrentType(DimensionedType):
    UNITS = ('mA', 'A', 'kA')
    DEFAULT = UNITS[1]

    def __init__(self, value, unit):
        super().__init__(value, unit)

    @property
    def value_a(self):
        return self['value']

    @property
    def value_ka(self):
        return self['value']/1000

    def _normalize(self):
        if self['unit'] == CurrentType.UNITS[1]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == CurrentType.UNITS[2]:
            self['value'] = self['value']*1000
        elif self['unit'] == CurrentType.UNITS[0]:
            self['value'] = self['value']/1000
        else:
            pass
        self['unit'] = CurrentType.UNITS[1]


class PowerType(DimensionedType):
    UNITS = ['mW', 'W', 'kW']
    DEFAULT = UNITS[1]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    @property
    def value_w(self):
        return self['value']

    @property
    def value_kw(self):
        return self['value']/1000

    def _normalize(self):
        if self['unit'] == PowerType.UNITS[1]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == PowerType.UNITS[2]:
            self['value'] = self['value']*1000
        elif self['unit'] == PowerType.UNITS[0]:
            self['value'] = self['value']/1000
        else:
            pass
        self['unit'] = PowerType.UNITS[1]


class ReactivePowerType(DimensionedType):
    UNITS = ('var', 'kvar')
    DEFAULT = UNITS[0]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    def _normalize(self):
        if self['unit'] == ReactivePowerType.UNITS[0]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == ReactivePowerType.UNITS[1]:
            self['value'] = self['value']*1000
        else:
            pass
        self['unit'] = ReactivePowerType.UNITS[0]


class ApparentPowerType(DimensionedType):
    UNITS = ('VA', 'kVA')
    DEFAULT = UNITS[0]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    def _normalize(self):
        if self['unit'] == ApparentPowerType.UNITS[0]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == ApparentPowerType.UNITS[1]:
            self['value'] = self['value']*1000
        else:
            pass
        self['unit'] = ApparentPowerType.UNITS[0]


class FrequencyType(DimensionedType):
    UNITS = ('Hz', 'kHz')
    DEFAULT = UNITS[0]

    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    @property
    def value_hz(self):
        return self['value']

    def _normalize(self):
        if self['unit'] == FrequencyType.UNITS[0]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == FrequencyType.UNITS[1]:
            self['value'] = self['value']*1000
        else:
            pass
        self['unit'] = FrequencyType.UNITS[0]


class TemperatureType(DimensionedType):
    UNITS = ('℃', 'F', 'K')
    DEFAULT = UNITS[0]

    def __init__(self, value, unit):
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
        return float(self['value'] + 273.15)

    def _normalize(self):
        if self['unit'] == TemperatureType.UNITS[0]:
            return
        self['original_value'] = self['value']
        self['original_unit'] = self['unit']
        if self['unit'] == TemperatureType.UNITS[1]:
            self['value'] = float(self['value'] - 32) * 5 / 9
        elif self['unit'] == TemperatureType.UNITS[2]:
            self['value'] = float(self['value']) - 273.15

        self['unit'] = TemperatureType.UNITS[0]


class CurrencyType(DimensionedType):
    def __init__(self, value, unit):
        super().__init__(value, unit)
        self._normalize()

    def _normalize(self):
        pass


class DateTimeType():
    def __init__(self, value, t_z: tzinfo = None):
        self._timestamp = value
        self._datetime = datetime.fromtimestamp(int(value) / 1e3, t_z)

    def date(self):
        return self._datetime.date

    def time(self):
        return self._datetime.time

    def timestamp(self):
        return self._datetime.timestamp

    def timezone(self):
        return self._datetime.tzname

    def __str__(self):
        return str(self._datetime) + f" ({self.__class__.__name__})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._datetime == other._datetime
        else:
            return False


class EnumType(UserDict):

    def __init__(self, value: IntEnum):
        if isinstance(value, IntEnum):
            super().__init__(
                {'value': value.value, 'name': value.name.title()})
        else:
            raise TypeError(f"{value} not of type IntEnum")


class ListType(UserList):
    def __init__(self, value):
        if type(value) is list:
            super().__init__(value)
            self._normalize()
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

    def _normalize(self):
        for d in self.data:
            if '_normalize' in dir(d):
                d._normalize()


class DictType(UserDict):
    def __str__(self) -> str:
        out = "{\n"
        for k in self.keys():
            out += f"  {k}: {self[k]}\n"
        out += "}"
        return out


class SolisDataFactory:
    """ Convert input dict from API into dict of values
    Keys get normalized to snake_case
    Dimensioned values get parsed, converted and/or normalized
    Unused k/v pairs get dropped
    Values may be again be dict or list
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
        for key in keys:
            new_key = pattern.sub('_', key).lower()
            # Fix 'InCome' wrongly converted into 'in_come'
            new_key = re.sub(r'in_come', 'income', new_key)

            if not SolisDataFactory._key_is_unit(key):
                value = input[key]
                nr_of_strings = 0
                unit = None
                if key+'Str' in keys:
                    unit = input[key+'Str']
                elif key+'Unit' in keys:
                    unit = input[key+'Unit']
                try:
                    if new_key[-6:] == 'income':
                        unit = input['money']
                except KeyError:
                    pass
                try:
                    if unit is None:
                        if new_key[-4:] == 'time':
                            unit = input['timeZoneStr']
                except KeyError:
                    pass
                try:
                    if new_key[-9:] == 'timestamp':
                        s = re.split(r'/s', value)
                        value = s[0]
                        if len(s) > 1:
                            unit = s[-1]
                except KeyError:
                    pass
                try:
                    nr_of_strings = input['dcInputtype'] + 1
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
        if unit is not None:
            re_datetime = '_time$|_timestamp$|__date$'
            match(unit):
                case unit if unit in EnergyType.UNITS:
                    p = EnergyType(value, unit)
                case unit if unit in VoltageType.UNITS:
                    p = VoltageType(value, unit)
                case unit if unit in CurrentType.UNITS:
                    p = CurrentType(value, unit)
                case unit if unit in PowerType.UNITS:
                    p = PowerType(value, unit)
                case unit if unit in ReactivePowerType.UNITS:
                    p = ReactivePowerType(value, unit.lower())
                case unit if unit in ApparentPowerType.UNITS:
                    p = ApparentPowerType(value, unit)
                case unit if unit in FrequencyType.UNITS:
                    p = FrequencyType(value, unit)
                case _ if key[-11:] == 'temperature':
                    p = TemperatureType(value, unit)
                case _ if re.search('_income', key, re.IGNORECASE) is not None:
                    p = CurrencyType(value, unit)
                case _ if re.search(re_datetime, key, re.IGNORECASE)\
                        is not None:
                    try:
                        regex = '.*UTC([+\-]?)(\d{2}):(\d{2})'  # noqa: W605
                        sign, hours, minutes = re.match(regex, unit).groups()
                        sign = -1 if sign == '-' else 1
                        hours, minutes = int(hours), int(minutes)
                        tzinfo = timezone(sign * timedelta(hours=hours, minutes=minutes))  # noqa: E501
                        p = DateTimeType(value, tzinfo)
                    except AttributeError:
                        p = DateTimeType(value)
                case _:
                    p = GenericType(value, unit)
        else:
            match(key):
                case 'state':
                    p = EnumType(State(value))
                case 'state_exception_flag':
                    p = EnumType(InverterOfflineState(value))
                case 'type':
                    match(type):
                        case EntityType.PLANT:
                            p = EnumType(PlantType(value))
                        case EntityType.INVERTER:
                            p = EnumType(InverterType(value))
                        case _:
                            p = value
                case _ if re.search('_pec', key, re.IGNORECASE) is not None:
                    p = value
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
                case _ if re.search('looked_power', key, re.IGNORECASE)\
                        is not None:
                    p = ApparentPowerType(value, ApparentPowerType.DEFAULT)
                case _ if re.search('reactive_power', key, re.IGNORECASE)\
                        is not None:
                    p = ReactivePowerType(value, ReactivePowerType.DEFAULT)
                case _ if re.search(r"power_?\d{1,2}$", key, re.IGNORECASE)\
                        is not None:
                    p = PowerType(value, PowerType.DEFAULT)
                case _ if re.search(r"_pow$", key, re.IGNORECASE) is not None:
                    p = PowerType(value, PowerType.DEFAULT)
                case _ if re.search(r"_time$", key, re.IGNORECASE) is not None:
                    p = DateTimeType(value)
                case _ if re.search(r"_timestamp$", key, re.IGNORECASE)\
                        is not None:
                    p = DateTimeType(value)
                case _ if re.search(r"_date$", key, re.IGNORECASE) is not None:
                    p = DateTimeType(value)
                case _:
                    if unit is not None:
                        p = GenericType(value, unit)
                    else:
                        p = value
        return p
