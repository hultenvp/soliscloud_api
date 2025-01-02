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
async def test_user_station_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.user_station_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.USER_STATION_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})
    assert result == VALID_RESPONSE

    # All arguments filled
    result = await api_instance.user_station_list(
        KEY, SECRET,
        page_no=4, page_size=100, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.USER_STATION_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 100, 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_user_station_list_invalid_page_size(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.user_station_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_station_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_detail(KEY, SECRET, station_id=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_DETAIL, KEY, SECRET, {'id': 1000})

    # All arguments filled
    result = await api_instance.station_detail(
        KEY, SECRET,
        station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_DETAIL,
        KEY, SECRET,
        {'id': 1000, 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_station_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_day(
        KEY, SECRET,
        currency='EUR', time='2023-01-01', time_zone=1, station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_DAY,
        KEY, SECRET,
        {'money': 'EUR', 'time': '2023-01-01', 'timeZone': 1, 'id': '1000'})

    result = await api_instance.station_day(
        KEY, SECRET,
        currency='EUR', time='2023-01-01', time_zone=1, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_DAY,
        KEY, SECRET,
        {'money': 'EUR', 'time': '2023-01-01', 'timeZone': 1, 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_day_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(
            KEY, SECRET,
            currency='EUR', time='2023-01-01', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(
            KEY, SECRET,
            currency='EUR',
            time='2023-01-01',
            time_zone=1,
            station_id='1000',
            nmi_code=NMI)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(
            KEY, SECRET,
            currency='EUR', time='2023', time_zone=1, station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(
            KEY, SECRET,
            currency='EUR', time='2023+01-01', time_zone=1, station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(
            KEY, SECRET,
            currency='EUR', time='2023-01+01', time_zone=1, station_id='1000')


@pytest.mark.asyncio
async def test_station_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_month(
        KEY, SECRET,
        currency='EUR', month='2023-01', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_MONTH,
        KEY, SECRET,
        {'money': 'EUR', 'month': '2023-01', 'id': '1000'})

    result = await api_instance.station_month(
        KEY, SECRET,
        currency='EUR', month='2023-01', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_MONTH,
        KEY, SECRET,
        {'money': 'EUR', 'month': '2023-01', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_month_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(
            KEY, SECRET,
            currency='EUR', month='2023-01')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(
            KEY, SECRET,
            currency='EUR', month='2023-01', station_id='1000', nmi_code=NMI)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(
            KEY, SECRET,
            currency='EUR', month='2023', station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(
            KEY, SECRET,
            currency='EUR', month='2023+01', station_id='1000')


@pytest.mark.asyncio
async def test_station_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_year(
        KEY, SECRET,
        currency='EUR', year='2023', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_YEAR,
        KEY, SECRET,
        {'money': 'EUR', 'year': '2023', 'id': '1000'})

    result = await api_instance.station_year(
        KEY, SECRET,
        currency='EUR', year='2023', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_YEAR,
        KEY, SECRET,
        {'money': 'EUR', 'year': '2023', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_year_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(
            KEY, SECRET,
            currency='EUR', year='2023')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(
            KEY, SECRET,
            currency='EUR', year='2023', station_id='1000', nmi_code=NMI)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(
            KEY, SECRET,
            currency='EUR', year='22023', station_id='1000')


@pytest.mark.asyncio
async def test_station_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_all(
        KEY, SECRET,
        currency='EUR', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_ALL, KEY, SECRET, {'money': 'EUR', 'id': '1000'})

    result = await api_instance.station_all(
        KEY, SECRET,
        currency='EUR', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.STATION_ALL, KEY, SECRET, {'money': 'EUR', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_all_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_all(KEY, SECRET, currency='EUR')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_all(
            KEY, SECRET,
            currency='EUR', station_id='1000', nmi_code=NMI)


@pytest.mark.asyncio
async def test_station_detail_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_detail_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_DETAIL_LIST,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.station_detail_list(
        KEY, SECRET,
        page_no=4, page_size=30)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_DETAIL_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30})


@pytest.mark.asyncio
async def test_station_detail_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_detail_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_station_day_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_day_energy_list(
        KEY, SECRET,
        time='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_DAY_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20, 'time': '2023-01-01'})

    result = await api_instance.station_day_energy_list(
        KEY, SECRET,
        page_no=4, page_size=30, time='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_DAY_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30, 'time': '2023-01-01'})


@pytest.mark.asyncio
async def test_station_day_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(
            KEY, SECRET,
            page_size=1000, time='2023-01-01')
    # Wrong time format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(
            KEY, SECRET,
            time='2023')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(
            KEY, SECRET,
            time='2023+01-01')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(
            KEY, SECRET,
            time='2023-01+01')


@pytest.mark.asyncio
async def test_station_month_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_month_energy_list(
        KEY, SECRET,
        month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_MONTH_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20, 'time': '2023-01'})

    result = await api_instance.station_month_energy_list(
        KEY, SECRET,
        page_no=4, page_size=30, month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_MONTH_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30, 'time': '2023-01'})


@pytest.mark.asyncio
async def test_station_month_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(
            KEY, SECRET,
            page_size=1000, month='2023-01')
    # Wrong month format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(
            KEY, SECRET,
            month='2023')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(
            KEY, SECRET,
            month='2023+01')


@pytest.mark.asyncio
async def test_station_year_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_year_energy_list(
        KEY, SECRET,
        year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_YEAR_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20, 'time': '2023'})

    result = await api_instance.station_year_energy_list(
        KEY, SECRET,
        page_no=4, page_size=30, year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.STATION_YEAR_ENERGY_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30, 'time': '2023'})


@pytest.mark.asyncio
async def test_station_year_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_year_energy_list(
            KEY, SECRET,
            page_size=1000, year='2023')
    # Wrong year format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.station_year_energy_list(
            KEY, SECRET,
            year='22023')
