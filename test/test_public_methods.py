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
async def test_collector_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.collector_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.COLLECTOR_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    # All arguments filled
    result = await api_instance.collector_list(
        KEY,
        SECRET,
        page_no=4, page_size=100, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.COLLECTOR_LIST,
        KEY, SECRET,
        {
            'pageNo': 4,
            'pageSize': 100,
            'stationId': 1000,
            'nmiCode': 'nmi_code'
        })


@pytest.mark.asyncio
async def test_collector_list_invalid_page_size(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_collector_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.collector_detail(
        KEY, SECRET, collector_sn=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.COLLECTOR_DETAIL, KEY, SECRET, {'sn': 1000})

    result = await api_instance.collector_detail(
        KEY, SECRET, collector_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.COLLECTOR_DETAIL, KEY, SECRET, {'id': '1000'})


@pytest.mark.asyncio
async def test_collector_detail_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_detail(
            KEY, SECRET,
            collector_sn=1000, collector_id='1000')


@pytest.mark.asyncio
async def test_collector_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.collector_day(
        KEY, SECRET,
        collector_sn=1000, time='2023-01-01', time_zone=1)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.COLLECTOR_DAY,
        KEY, SECRET,
        {'sn': 1000, 'time': '2023-01-01', 'timeZone': 1})


@pytest.mark.asyncio
async def test_collector_day_invalid_params(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_day(
            KEY, SECRET,
            collector_sn=None, time='2023-01-01', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_day(
            KEY, SECRET,
            collector_sn='1000', time='2023', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_day(
            KEY, SECRET,
            collector_sn='1000', time='2023+01-01', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.collector_day(
            KEY, SECRET,
            collector_sn='1000', time='2023-01+01', time_zone=1)


@pytest.mark.asyncio
async def test_alarm_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.alarm_list(
        KEY, SECRET,
        station_id='1000', begintime='2022-01-01', endtime='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.ALARM_LIST,
        KEY, SECRET,
        {
            'pageNo': 1,
            'pageSize': 20,
            'stationId': '1000',
            'alarmBeginTime': '2022-01-01',
            'alarmEndTime': '2023-01-01'})

    result = await api_instance.alarm_list(
        KEY, SECRET,
        device_sn='1000', begintime='2022-01-01', endtime='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.ALARM_LIST,
        KEY, SECRET,
        {
            'pageNo': 1,
            'pageSize': 20,
            'alarmDeviceSn': '1000',
            'alarmBeginTime': '2022-01-01',
            'alarmEndTime': '2023-01-01'})

    result = await api_instance.alarm_list(
        KEY, SECRET,
        page_no=4,
        page_size=30,
        device_sn='1000',
        begintime='2022-01-01',
        endtime='2023-01-01',
        nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.ALARM_LIST,
        KEY, SECRET,
        {
            'pageNo': 4,
            'pageSize': 30,
            'alarmDeviceSn': '1000',
            'alarmBeginTime': '2022-01-01',
            'alarmEndTime': '2023-01-01',
            'nmiCode': NMI})


@pytest.mark.asyncio
async def test_alarm_list_invalid_params(api_instance):
    # Wrong page size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            page_size=1000,
            station_id='1000',
            begintime='2022-01-01',
            endtime='2023-01-01')
    # No Id and no Sn
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01-01', endtime='2023-01-01')
    # Both Id and Sn
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01-01',
            endtime='2023-01-01',
            station_id='1000',
            device_sn='sn')
    # Illegal begin time
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022',
            endtime='2023-01-01',
            station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022+01-01', endtime='2023-01-01', station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01+01',
            endtime='2023-01-01',
            station_id='1000')
    # Illegal end time
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01-01', endtime='2023', station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01-01', endtime='2023+01-01', station_id='1000')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.alarm_list(
            KEY, SECRET,
            begintime='2022-01-01', endtime='2023-01+01', station_id='1000')


@pytest.mark.asyncio
async def test_epm_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_LIST,
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.epm_list(
        KEY, SECRET,
        page_no=4, page_size=30, station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_LIST,
        KEY, SECRET,
        {'pageNo': 4, 'pageSize': 30, 'stationId': '1000'})


@pytest.mark.asyncio
async def test_epm_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_epm_detail(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_detail(KEY, SECRET, epm_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_DETAIL,
        KEY, SECRET,
        {'sn': 'sn'})


@pytest.mark.asyncio
async def test_epm_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_day(
        KEY, SECRET,
        searchinfo='info', epm_sn='sn', time='2023-01-01', time_zone=1)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_DAY,
        KEY, SECRET,
        {
            'searchinfo': 'info',
            'sn': 'sn',
            'time': '2023-01-01',
            'timezone': 1
        })


@pytest.mark.asyncio
async def test_epm_day_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(
            KEY, SECRET,
            searchinfo='info', epm_sn='sn', time='2023', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(
            KEY, SECRET,
            searchinfo='info', epm_sn='sn', time='2023+01-01', time_zone=1)

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(
            KEY, SECRET,
            searchinfo='info', epm_sn='sn', time='2023-01+01', time_zone=1)


@pytest.mark.asyncio
async def test_epm_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_month(
        KEY, SECRET, epm_sn='sn', month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_MONTH,
        KEY, SECRET,
        {'sn': 'sn', 'month': '2023-01'})


@pytest.mark.asyncio
async def test_epm_month_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_month(
            KEY, SECRET,
            epm_sn='sn', month='2023')

    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_month(
            KEY, SECRET,
            epm_sn='sn', month='2023+01')


@pytest.mark.asyncio
async def test_epm_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_year(
        KEY, SECRET,
        epm_sn='sn', year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_YEAR,
        KEY, SECRET,
        {'sn': 'sn', 'year': '2023'})


@pytest.mark.asyncio
async def test_epm_year_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.epm_year(
            KEY, SECRET,
            epm_sn='sn', year='22023')


@pytest.mark.asyncio
async def test_epm_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_all(KEY, SECRET, epm_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.EPM_ALL, KEY, SECRET, {'sn': 'sn'})


@pytest.mark.asyncio
async def test_weather_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.weather_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.WEATHER_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    # All arguments filled
    result = await api_instance.weather_list(
        KEY, SECRET,
        page_no=4, page_size=100, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(
        api.WEATHER_LIST,
        KEY, SECRET,
        {
            'pageNo': 4,
            'pageSize': 100,
            'stationId': 1000,
            'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_weather_list_invalid_page_size(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.weather_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_weather_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.weather_detail(KEY, SECRET, instrument_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(
        api.WEATHER_DETAIL, KEY, SECRET, {'sn': 'sn'})


@pytest.mark.asyncio
async def test_weather_detail_invalid_params(api_instance):
    with pytest.raises(api.SoliscloudAPI.SolisCloudError):
        await api_instance.weather_detail(
            KEY, SECRET,
            instrument_sn=None)
