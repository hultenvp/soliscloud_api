import pytest
import asyncio
import time
from datetime import datetime
from datetime import timezone
from aiohttp import ClientError
from soliscloud_api import SoliscloudAPI
from .const import KEY, SECRET, VALID_RESPONSE

VALID_HEADER = {
    'Content-MD5': 'U0Xj//qmRi3zoyapfAAuXw==',
    'Content-Type': 'application/json',
    'Date': 'Sun, 01 Jan 2023 00:00:00 GMT',
    'Authorization': 'API 1234567891234567890:8+oYgqSEFjxPaHIOgUKSpIdYCGU='
}

INVALID_RESPONSE_KEYERROR = {
    'succes': True,
    'codes': '0',
    'msg': 'success',
    'data': {'page': {'records': {'success': 1}}}
}


class MockedResponse():

    _body = None
    _httpstatus = None

    def __init__(self, body, status):
        self._body = body
        self._httpstatus = status

    async def json(self):
        return self._body

    async def release(self):
        return

    @property
    def status(self):
        return self._httpstatus


VALID_HTTP_RESPONSE = MockedResponse(VALID_RESPONSE, 200)
HTTP_RESPONSE_KEYERROR = MockedResponse(INVALID_RESPONSE_KEYERROR, 200)


@pytest.fixture
def api_instance():
    instance = SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance


def test_prepare_header(mocker):
    # Mock datetime to get deterministic result
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._now',
        return_value=datetime(2023, 1, 1, tzinfo=timezone.utc))
    header = SoliscloudAPI._prepare_header(
        '1234567891234567890',
        b'DEADBEEFDEADBEEFDEADBEEFDEADBEEF',
        {'pageNo': 1, 'pageSize': 100}, 'TEST')
    assert header == VALID_HEADER


@pytest.mark.asyncio
async def test_post_data_json(api_instance, mocker):
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._do_post_aiohttp',
        return_value=VALID_HTTP_RESPONSE)
    result = await api_instance._post_data_json(
        "/TEST",
        VALID_HEADER,
        {'test': 'test'})
    assert result == VALID_RESPONSE['data']


@pytest.mark.asyncio
async def test_post_data_json_throttled(api_instance, mocker):
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._do_post_aiohttp',
        return_value=VALID_HTTP_RESPONSE)
    # test max 2 calls per second
    iterations = 10
    start_time = time.time()
    for i in range(iterations):
        result = await api_instance._post_data_json(
            "/TEST",
            VALID_HEADER,
            {'test': 'test'})
    duration = time.time() - start_time
    print(f"Duration:  {duration:2f} seconds")
    assert duration >= (iterations/2)-1
    assert result == VALID_RESPONSE['data']


@pytest.mark.asyncio
async def test_post_data_json_fail(api_instance, mocker):
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._do_post_aiohttp',
        return_value=HTTP_RESPONSE_KEYERROR)
    with pytest.raises(SoliscloudAPI.ApiError):
        await api_instance._post_data_json(
            "/TEST",
            VALID_HEADER,
            {'test': 'test'})
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._do_post_aiohttp',
        return_value=VALID_HTTP_RESPONSE,
        side_effect=asyncio.TimeoutError)
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance._post_data_json(
            "/TEST",
            VALID_HEADER,
            {'test': 'test'})
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._do_post_aiohttp',
        return_value=VALID_HTTP_RESPONSE,
        side_effect=ClientError)
    with pytest.raises(SoliscloudAPI.SolisCloudError):
        await api_instance._post_data_json(
            "/TEST",
            VALID_HEADER,
            {'test': 'test'})


@pytest.mark.asyncio
async def test_get_data(api_instance, mocker):
    mocker.patch.object(
        api_instance,
        '_post_data_json',
        return_value=VALID_RESPONSE)
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._prepare_header',
        return_value=VALID_HEADER)
    result = await api_instance._get_data(
        "/TEST",
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 100})
    api_instance._post_data_json.assert_called_with(
        'https://soliscloud_test.com:13333/TEST',
        VALID_HEADER,
        {'pageNo': 1, 'pageSize': 100})
    assert result == VALID_RESPONSE


@pytest.mark.asyncio
async def test_get_records(api_instance, mocker):
    mocker.patch.object(
        api_instance,
        '_post_data_json',
        return_value=VALID_RESPONSE['data'])
    mocker.patch(
        'soliscloud_api.SoliscloudAPI._prepare_header',
        return_value=VALID_HEADER)
    result = await api_instance._get_records(
        "/TEST",
        KEY, SECRET,
        {'pageNo': 1, 'pageSize': 100})
    api_instance._post_data_json.assert_called_with(
        'https://soliscloud_test.com:13333/TEST',
        VALID_HEADER,
        {'pageNo': 1, 'pageSize': 100})
    assert result == VALID_RESPONSE['data']['page']['records']
