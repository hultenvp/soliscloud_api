"""Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/soliscloud_api
"""
from .client import SoliscloudAPI  # noqa: F401
from .client import SoliscloudError, SoliscloudHttpError  # noqa: F401
from .client import SoliscloudTimeoutError, SoliscloudApiError  # noqa: F401
from .entities import Plant, Inverter, Collector  # noqa: F401
from .types import (  # noqa: F401
    EntityType,
    State,
    InverterOfflineState,
    InverterType,
    PlantType,
    CollectorState
)
from .helpers import Helpers  # noqa: F401

# VERSION
VERSION = '1.3.0'
__version__ = VERSION

