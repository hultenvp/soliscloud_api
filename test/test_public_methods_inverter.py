import pytest
import soliscloud_api as api

# from soliscloud_api import *
from .const import KEY, SECRET, NMI, VALID_RESPONSE


@pytest.fixture
def api_instance():
    instance = api.SoliscloudAPI('https://soliscloud_test.com:13333', 1)

    return instance


@pytest.fixture
def patched_api(api_instance, mocker):
    mocked_class = mocker.create_autospec(api.SoliscloudAPI)
    mocker.patch.object(mocked_class, '_get_records',
                        return_value=VALID_RESPONSE)
    mocker.patch.object(mocked_class, '_get_data', return_value=VALID_RESPONSE)
    mocker.patch.object(api_instance, '_get_records',
                        mocked_class._get_records)
    mocker.patch.object(api_instance, '_get_data', mocked_class._get_data)

    return mocked_class


@pytest.mark.asyncio
async def test_inverter_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    # All arguments filled
    result = await api_instance.inverter_list(
        KEY, SECRET,
        page_no=4, page_size=100, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_LIST,
        KEY, SECRET,
        {
            'pageNo': 4,
            'pageSize': 100,
            'stationId': 1000,
            'nmiCode':
            'nmi_code'})


@pytest.mark.asyncio
async def test_inverter_list_invalid_page_size(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_inverter_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_detail(KEY, SECRET, inverter_sn=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_DETAIL, KEY, SECRET, {'sn': 1000})

    result = await api_instance.inverter_detail(
        KEY, SECRET,
        inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_DETAIL, KEY, SECRET, {'id': '1000'})


@pytest.mark.asyncio
async def test_inverter_detail_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_detail(
            KEY, SECRET,
            inverter_sn=1000, inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_day(
        KEY, SECRET,
        currency='EUR', time='2023-01-01', time_zone=1, inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_DAY,
        KEY, SECRET,
        {'money': 'EUR', 'time': '2023-01-01', 'timeZone': 1, 'id': '1000'})

    result = await api_instance.inverter_day(
        KEY, SECRET,
        currency='EUR', time='2023-01-01', time_zone=1, inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_DAY,
        KEY, SECRET,
        {'money': 'EUR', 'time': '2023-01-01', 'timeZone': 1, 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_day_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(
            KEY, SECRET,
            currency='EUR', time='2023-01-01', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(
            KEY, SECRET,
            currency='EUR',
            time='2023-01-01',
            time_zone=1,
            inverter_id='1000',
            inverter_sn='sn')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(
            KEY, SECRET,
            currency='EUR', time='2023', time_zone=1, inverter_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(
            KEY, SECRET,
            currency='EUR', time='2023+01-01', time_zone=1, inverter_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(
            KEY, SECRET,
            currency='EUR', time='2023-01+01', time_zone=1, inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_month(
        KEY, SECRET,
        currency='EUR', month='2023-01', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_MONTH,
        KEY, SECRET,
        {'money': 'EUR', 'month': '2023-01', 'id': '1000'})

    result = await api_instance.inverter_month(
        KEY, SECRET,
        currency='EUR', month='2023-01', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_MONTH,
        KEY, SECRET,
        {'money': 'EUR', 'month': '2023-01', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_month_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(
            KEY, SECRET,
            currency='EUR', month='2023-01')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(
            KEY, SECRET,
            currency='EUR',
            month='2023-01',
            inverter_id='1000',
            inverter_sn='sn')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(
            KEY, SECRET,
            currency='EUR', month='2023', inverter_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(
            KEY, SECRET,
            currency='EUR', month='2023+01', inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_year(
        KEY, SECRET,
        currency='EUR', year='2023', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_YEAR,
        KEY, SECRET,
        {'money': 'EUR', 'year': '2023', 'id': '1000'})

    result = await api_instance.inverter_year(
        KEY, SECRET,
        currency='EUR', year='2023', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_YEAR,
        KEY, SECRET,
        {'money': 'EUR', 'year': '2023', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_year_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(
            KEY, SECRET,
            currency='EUR', year='2023')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(
            KEY, SECRET,
            currency='EUR', year='2023', inverter_id='1000', inverter_sn='sn')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(
            KEY, SECRET,
            currency='EUR', year='22023', inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_all(
        KEY, SECRET,
        currency='EUR', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_ALL,
        KEY, SECRET,
        {'money': 'EUR', 'id': '1000'})

    result = await api_instance.inverter_all(
        KEY, SECRET,
        currency='EUR', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.INVERTER_ALL,
        KEY, SECRET,
        {'money': 'EUR', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_all_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_all(KEY, SECRET, currency='EUR')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_all(
            KEY, SECRET,
            currency='EUR', inverter_id='1000', inverter_sn='sn')


@pytest.mark.asyncio
async def test_inverter_detail_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_detail_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_DETAIL_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.inverter_detail_list(
        KEY, SECRET,
        page_no=4, page_size=30)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_DETAIL_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30})


@pytest.mark.asyncio
async def test_inverter_detail_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_detail_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_inverter_shelf_time(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_shelf_time(
        KEY, SECRET,
        inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_SHELF_TIME,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20, 'sn': 'sn'})

    # Optional arguments
    result = await api_instance.inverter_shelf_time(
        KEY, SECRET,
        page_no=50, page_size=50, inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.INVERTER_SHELF_TIME,
        KEY, SECRET,
        {'pageNo': 50, 'pageSize': 50, 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_shelf_time_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_shelf_time(
            KEY, SECRET,
            page_size=1000, inverter_sn='sn')

    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_shelf_time(KEY, SECRET, inverter_sn=None)
