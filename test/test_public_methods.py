import pytest

from soliscloud_api import *
from .const import KEY, SECRET, NMI, VALID_RESPONSE


@pytest.fixture
def api_instance():
    instance = SoliscloudAPI('https://soliscloud_test.com:13333', 1)

    return instance


@pytest.fixture
def patched_api(api_instance, mocker):
    mocked_class = mocker.create_autospec(SoliscloudAPI)
    mocker.patch.object(mocked_class, '_get_records', return_value=VALID_RESPONSE)
    mocker.patch.object(mocked_class, '_get_data', return_value=VALID_RESPONSE)
    mocker.patch.object(api_instance, '_get_records', mocked_class._get_records)
    mocker.patch.object(api_instance, '_get_data', mocked_class._get_data)

    return mocked_class


@pytest.mark.asyncio
async def test_user_station_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.user_station_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(USER_STATION_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})
    assert result == VALID_RESPONSE

    # All arguments filled
    result = await api_instance.user_station_list(KEY, SECRET, page_no=4, page_size=100, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(USER_STATION_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 100,
                                                                                 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_user_station_list_invalid_page_size(api_instance):
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.user_station_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_station_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_detail(KEY, SECRET, station_id=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_DETAIL, KEY, SECRET, {'id': 1000})

    # All arguments filled
    result = await api_instance.station_detail(KEY, SECRET, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_DETAIL, KEY, SECRET, {'id': 1000, 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_collector_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.collector_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(COLLECTOR_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    # All arguments filled
    result = await api_instance.collector_list(KEY, SECRET, page_no=4, page_size=100, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(COLLECTOR_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 100,
                                                                              'stationId': 1000, 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_collector_list_invalid_page_size(api_instance):
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.collector_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_collector_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.collector_detail(KEY, SECRET, collector_sn=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(COLLECTOR_DETAIL, KEY, SECRET, {'sn': 1000})

    result = await api_instance.collector_detail(KEY, SECRET, collector_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(COLLECTOR_DETAIL, KEY, SECRET, {'id': '1000'})


@pytest.mark.asyncio
async def test_collector_detail_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.collector_detail(KEY, SECRET, collector_sn=1000, collector_id='1000')


@pytest.mark.asyncio
async def test_inverter_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(INVERTER_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    # All arguments filled
    result = await api_instance.inverter_list(KEY, SECRET, page_no=4, page_size=100, station_id=1000, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(INVERTER_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 100,
                                                                             'stationId': 1000, 'nmiCode': 'nmi_code'})


@pytest.mark.asyncio
async def test_inverter_list_invalid_page_size(api_instance):
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_list(KEY, SECRET, page_size=101)


@pytest.mark.asyncio
async def test_inverter_detail_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_detail(KEY, SECRET, inverter_sn=1000)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_DETAIL, KEY, SECRET, {'sn': 1000})

    result = await api_instance.inverter_detail(KEY, SECRET, inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_DETAIL, KEY, SECRET, {'id': '1000'})


@pytest.mark.asyncio
async def test_inverter_detail_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_detail(KEY, SECRET, inverter_sn=1000, inverter_id='1000')


@pytest.mark.asyncio
async def test_station_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1, station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_DAY, KEY, SECRET, {'money': 'EUR', 'time': '2023-01-01',
                                                                        'timeZone': 1, 'id': '1000'})

    result = await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1, nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_DAY, KEY, SECRET, {'money': 'EUR', 'time': '2023-01-01',
                                                                        'timeZone': 1, 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_day_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1,
                                       station_id='1000', nmi_code=NMI)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023', time_zone=1, station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023+01-01', time_zone=1, station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day(KEY, SECRET, currency='EUR', time='2023-01+01', time_zone=1, station_id='1000')


@pytest.mark.asyncio
async def test_station_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023-01', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_MONTH, KEY, SECRET, {'money': 'EUR', 'month': '2023-01', 'id': '1000'})

    result = await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023-01', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_MONTH, KEY, SECRET, {'money': 'EUR', 'month': '2023-01', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_month_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023-01')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023-01', station_id='1000', nmi_code=NMI)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023', station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month(KEY, SECRET, currency='EUR', month='2023+01', station_id='1000')


@pytest.mark.asyncio
async def test_station_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_year(KEY, SECRET, currency='EUR', year='2023', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_YEAR, KEY, SECRET, {'money': 'EUR', 'year': '2023', 'id': '1000'})

    result = await api_instance.station_year(KEY, SECRET, currency='EUR', year='2023', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_YEAR, KEY, SECRET, {'money': 'EUR', 'year': '2023', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_year_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(KEY, SECRET, currency='EUR', year='2023')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(KEY, SECRET, currency='EUR', year='2023', station_id='1000', nmi_code=NMI)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_year(KEY, SECRET, currency='EUR', year='22023', station_id='1000')


@pytest.mark.asyncio
async def test_station_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_all(KEY, SECRET, currency='EUR', station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_ALL, KEY, SECRET, {'money': 'EUR', 'id': '1000'})

    result = await api_instance.station_all(KEY, SECRET, currency='EUR', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(STATION_ALL, KEY, SECRET, {'money': 'EUR', 'nmiCode': NMI})


@pytest.mark.asyncio
async def test_station_all_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_all(KEY, SECRET, currency='EUR')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_all(KEY, SECRET, currency='EUR', station_id='1000', nmi_code=NMI)


@pytest.mark.asyncio
async def test_inverter_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1, inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_DAY, KEY, SECRET, {'money': 'EUR', 'time': '2023-01-01',
                                                                         'timeZone': 1, 'id': '1000'})

    result = await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1, inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_DAY, KEY, SECRET, {'money': 'EUR', 'time': '2023-01-01',
                                                                         'timeZone': 1, 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_day_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023-01-01', time_zone=1,
                                        inverter_id='1000', inverter_sn='sn')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023', time_zone=1, inverter_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023+01-01', time_zone=1, inverter_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_day(KEY, SECRET, currency='EUR', time='2023-01+01', time_zone=1, inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023-01', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_MONTH, KEY, SECRET, {'money': 'EUR', 'month': '2023-01', 'id': '1000'})

    result = await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023-01', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_MONTH, KEY, SECRET, {'money': 'EUR', 'month': '2023-01', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_month_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023-01')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023-01', inverter_id='1000', inverter_sn='sn')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023', inverter_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_month(KEY, SECRET, currency='EUR', month='2023+01', inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_year(KEY, SECRET, currency='EUR', year='2023', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_YEAR, KEY, SECRET, {'money': 'EUR', 'year': '2023', 'id': '1000'})

    result = await api_instance.inverter_year(KEY, SECRET, currency='EUR', year='2023', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_YEAR, KEY, SECRET, {'money': 'EUR', 'year': '2023', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_year_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(KEY, SECRET, currency='EUR', year='2023')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(KEY, SECRET, currency='EUR', year='2023', inverter_id='1000', inverter_sn='sn')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_year(KEY, SECRET, currency='EUR', year='22023', inverter_id='1000')


@pytest.mark.asyncio
async def test_inverter_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_all(KEY, SECRET, currency='EUR', inverter_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_ALL, KEY, SECRET, {'money': 'EUR', 'id': '1000'})

    result = await api_instance.inverter_all(KEY, SECRET, currency='EUR', inverter_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_data.assert_called_with(INVERTER_ALL, KEY, SECRET, {'money': 'EUR', 'sn': 'sn'})


@pytest.mark.asyncio
async def test_inverter_all_invalid_params(api_instance):
    # ID and SN together
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_all(KEY, SECRET, currency='EUR')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_all(KEY, SECRET, currency='EUR', inverter_id='1000', inverter_sn='sn')


@pytest.mark.asyncio
async def test_inverter_alarm_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_alarm_list(KEY, SECRET, station_id='1000',
                                                    begintime='2022-01-01',
                                                    endtime='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(ALARM_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20, 'stationId': '1000',
                                                                          'alarmBeginTime': '2022-01-01',
                                                                          'alarmEndTime': '2023-01-01'})

    result = await api_instance.inverter_alarm_list(KEY, SECRET, device_sn='1000', begintime='2022-01-01',
                                                    endtime='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(ALARM_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20,
                                                                          'alarmDeviceSn': '1000',
                                                                          'alarmBeginTime': '2022-01-01',
                                                                          'alarmEndTime': '2023-01-01'})

    result = await api_instance.inverter_alarm_list(KEY, SECRET, page_no=4, page_size=30, device_sn='1000',
                                                    begintime='2022-01-01', endtime='2023-01-01', nmi_code=NMI)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(ALARM_LIST, KEY, SECRET, {'pageNo': 4,
                                                                          'pageSize': 30,
                                                                          'alarmDeviceSn': '1000',
                                                                          'alarmBeginTime': '2022-01-01',
                                                                          'alarmEndTime': '2023-01-01',
                                                                          'nmiCode': NMI})


@pytest.mark.asyncio
async def test_inverter_alarm_list_invalid_params(api_instance):
    # Wrong page size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, page_size=1000, station_id='1000',
                                               begintime='2022-01-01', endtime='2023-01-01')
    # No Id and no Sn
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01-01', endtime='2023-01-01')
    # Both Id and Sn
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01-01', endtime='2023-01-01',
                                               station_id='1000', device_sn='sn')
    # Illegal begin time
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022', endtime='2023-01-01', station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022+01-01', endtime='2023-01-01', station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01+01', endtime='2023-01-01', station_id='1000')
    # Illegal end time
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01-01', endtime='2023', station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01-01', endtime='2023+01-01', station_id='1000')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_alarm_list(KEY, SECRET, begintime='2022-01-01', endtime='2023-01+01', station_id='1000')


@pytest.mark.asyncio
async def test_station_detail_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_detail_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_DETAIL_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.station_detail_list(KEY, SECRET, page_no=4, page_size=30)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_DETAIL_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 30})


@pytest.mark.asyncio
async def test_station_detail_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_detail_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_inverter_detail_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.inverter_detail_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(INVERTER_DETAIL_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.inverter_detail_list(KEY, SECRET, page_no=4, page_size=30)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(INVERTER_DETAIL_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 30})


@pytest.mark.asyncio
async def test_inverter_detail_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.inverter_detail_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_station_day_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_day_energy_list(KEY, SECRET, time='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_DAY_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 1, 'pageSize': 20, 'time': '2023-01-01'})

    result = await api_instance.station_day_energy_list(KEY, SECRET, page_no=4, page_size=30, time='2023-01-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_DAY_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 4, 'pageSize': 30, 'time': '2023-01-01'})


@pytest.mark.asyncio
async def test_station_day_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(KEY, SECRET, page_size=1000, time='2023-01-01')
    # Wrong time format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(KEY, SECRET, time='2023')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(KEY, SECRET, time='2023+01-01')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_day_energy_list(KEY, SECRET, time='2023-01+01')


@pytest.mark.asyncio
async def test_station_month_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_month_energy_list(KEY, SECRET, month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_MONTH_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 1, 'pageSize': 20, 'time': '2023-01'})

    result = await api_instance.station_month_energy_list(KEY, SECRET, page_no=4, page_size=30, month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_MONTH_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 4, 'pageSize': 30, 'time': '2023-01'})


@pytest.mark.asyncio
async def test_station_month_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(KEY, SECRET, page_size=1000, month='2023-01')
    # Wrong month format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(KEY, SECRET, month='2023')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_month_energy_list(KEY, SECRET, month='2023+01')


@pytest.mark.asyncio
async def test_station_year_energy_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.station_year_energy_list(KEY, SECRET, year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_YEAR_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 1, 'pageSize': 20, 'time': '2023'})

    result = await api_instance.station_year_energy_list(KEY, SECRET, page_no=4, page_size=30, year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(STATION_YEAR_ENERGY_LIST, KEY, SECRET,
                                                {'pageNo': 4, 'pageSize': 30, 'time': '2023'})


@pytest.mark.asyncio
async def test_station_year_energy_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_year_energy_list(KEY, SECRET, page_size=1000, year='2023')
    # Wrong year format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.station_year_energy_list(KEY, SECRET, year='22023')


@pytest.mark.asyncio
async def test_epm_list_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_list(KEY, SECRET)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_LIST, KEY, SECRET, {'pageNo': 1, 'pageSize': 20})

    result = await api_instance.epm_list(KEY, SECRET, page_no=4, page_size=30, station_id='1000')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_LIST, KEY, SECRET, {'pageNo': 4, 'pageSize': 30, 'stationId': '1000'})


@pytest.mark.asyncio
async def test_epm_list_invalid_params(api_instance):
    # Wrong page_size
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_list(KEY, SECRET, page_size=1000)


@pytest.mark.asyncio
async def test_epm_detail(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_detail(KEY, SECRET, epm_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_DETAIL, KEY, SECRET, {'sn': 'sn'})


@pytest.mark.asyncio
async def test_epm_day_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_day(KEY, SECRET, searchinfo='info', epm_sn='sn', time='2023-01-01', time_zone=1)
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_DAY, KEY, SECRET,
                                                {'searchinfo': 'info', 'sn': 'sn', 'time': '2023-01-01', 'timezone': 1})


@pytest.mark.asyncio
async def test_epm_day_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(KEY, SECRET, searchinfo='info', epm_sn='sn', time='2023', time_zone=1)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(KEY, SECRET, searchinfo='info', epm_sn='sn', time='2023+01-01', time_zone=1)

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_day(KEY, SECRET, searchinfo='info', epm_sn='sn', time='2023-01+01', time_zone=1)


@pytest.mark.asyncio
async def test_epm_month_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_month(KEY, SECRET, epm_sn='sn', month='2023-01')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_MONTH, KEY, SECRET, {'sn': 'sn', 'month': '2023-01'})


@pytest.mark.asyncio
async def test_epm_month_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_month(KEY, SECRET, epm_sn='sn', month='2023')

    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_month(KEY, SECRET, epm_sn='sn', month='2023+01')


@pytest.mark.asyncio
async def test_epm_year_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_year(KEY, SECRET, epm_sn='sn', year='2023')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_YEAR, KEY, SECRET, {'sn': 'sn', 'year': '2023'})


@pytest.mark.asyncio
async def test_epm_year_invalid_params(api_instance):
    # Wrong time format
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance.epm_year(KEY, SECRET, epm_sn='sn', year='22023')


@pytest.mark.asyncio
async def test_epm_all_valid(api_instance, patched_api):
    # Required arguments only
    result = await api_instance.epm_all(KEY, SECRET, epm_sn='sn')
    assert result == VALID_RESPONSE
    patched_api._get_records.assert_called_with(EPM_ALL, KEY, SECRET, {'sn': 'sn'})
