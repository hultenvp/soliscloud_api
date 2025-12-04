import pytest
from soliscloud_api import Helpers
import soliscloud_api as api
from .const import (
    KEY,
    SECRET,
)

VALID_STATION_DATA = [
    {'id': 123456789, 'name': 'Station 1'},
    {'id': 987654321, 'name': 'Station 2'}
]

INVALID_STATION_DATA = [
    {'station_id': 123456789, 'name': 'Station 1'},
    {'station_id': 987654321, 'name': 'Station 2'}
]

VALID_INVERTER_DATA = [
    {'id': 123456789, 'name': 'Inverter 1'},
    {'id': 987654321, 'name': 'Inverter 2'}
]

INVALID_INVERTER_DATA = [
    {'inverter_id': 123456789, 'name': 'Inverter 1'},
    {'inverter_id': 987654321, 'name': 'Inverter 2'}
]


@pytest.fixture
def api_instance():
    instance = api.SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance


@pytest.mark.asyncio
async def test_helper_station_ids(api_instance, mocker):
    mocked_class = mocker.create_autospec(api.SoliscloudAPI)
    mocker.patch.object(mocked_class, 'user_station_list',
                        return_value=VALID_STATION_DATA)
    mocker.patch.object(api_instance, 'user_station_list', mocked_class.user_station_list)  # noqa: E501
    station_ids = await Helpers.get_station_ids(
        api_instance, KEY, SECRET)
    assert station_ids == (123456789, 987654321)
    mocker.patch.object(mocked_class, 'user_station_list',
                        return_value=INVALID_STATION_DATA)
    mocker.patch.object(api_instance, 'user_station_list', mocked_class.user_station_list)  # noqa: E501
    station_ids = await Helpers.get_station_ids(
        api_instance, KEY, SECRET)
    assert station_ids == ()
    mocker.patch.object(mocked_class, 'user_station_list',
                        return_value=None)
    mocker.patch.object(api_instance, 'user_station_list', mocked_class.user_station_list)  # noqa: E501
    station_ids = await Helpers.get_station_ids(
        api_instance, KEY, SECRET)
    assert station_ids is None


@pytest.mark.asyncio
async def test_helper_inverter_ids(api_instance, mocker):
    mocked_class = mocker.create_autospec(api.SoliscloudAPI)
    mocker.patch.object(mocked_class, 'inverter_list',
                        return_value=VALID_INVERTER_DATA)
    mocker.patch.object(api_instance, 'inverter_list', mocked_class.inverter_list)  # noqa: E501
    inverter_ids = await Helpers.get_inverter_ids(
        api_instance, KEY, SECRET)
    assert inverter_ids == (123456789, 987654321)
    mocker.patch.object(mocked_class, 'inverter_list',
                        return_value=INVALID_INVERTER_DATA)
    mocker.patch.object(api_instance, 'inverter_list', mocked_class.inverter_list)  # noqa: E501
    inverter_ids = await Helpers.get_inverter_ids(
        api_instance, KEY, SECRET)
    assert inverter_ids == ()
    mocker.patch.object(mocked_class, 'inverter_list',
                        return_value=None)
    mocker.patch.object(api_instance, 'inverter_list', mocked_class.inverter_list)  # noqa: E501
    inverter_ids = await Helpers.get_inverter_ids(
        api_instance, KEY, SECRET)
    assert inverter_ids is None
