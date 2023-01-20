import pytest
from datetime import datetime
from datetime import timezone
from aiohttp import ClientError, ClientSession
from unittest.mock import patch
import soliscloud_api.soliscloud_api as api

try:
    # Mock has been added to stdlib in Python 3.3.
    from unittest.mock import MagicMock, call
except ImportError:
    from mock import MagicMock, call

from .const import KEY, SECRET, NMI, VALID_RESPONSE

VALID_HEADER = {
    'Content-MD5': 'U0Xj//qmRi3zoyapfAAuXw==',
    'Content-Type': 'application/json',
    'Date': 'Sun, 01 Jan 2023 00:00:00 GMT',
    'Authorization': 'API 1234567891234567890:8+oYgqSEFjxPaHIOgUKSpIdYCGU='
}

@pytest.fixture
def api_instance():
    instance = api.SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance

def test_prepare_header(mocker):
    # Mock datetime to get deterministic result
    mocker.patch('soliscloud_api.soliscloud_api.SoliscloudAPI._now', return_value=datetime(2023,1,1,tzinfo=timezone.utc))
    header = api.SoliscloudAPI._prepare_header('1234567891234567890', b'DEADBEEFDEADBEEFDEADBEEFDEADBEEF', {'pageNo': 1, 'pageSize': 100}, 'TEST')
    assert header==VALID_HEADER

@pytest.mark.asyncio
async def test_post_data_json(api_instance, mocker):
    # Still to do
    pass

@pytest.mark.asyncio
async def test_get_data(api_instance, mocker):
    mocker.patch.object(api_instance, '_post_data_json', return_value = VALID_RESPONSE)
    mocker.patch('soliscloud_api.soliscloud_api.SoliscloudAPI._prepare_header', return_value=VALID_HEADER)
    result=await api_instance._get_data("/TEST", KEY, SECRET, {'pageNo': 1, 'pageSize': 100})
    api_instance._post_data_json.assert_called_with('https://soliscloud_test.com:13333/TEST', VALID_HEADER, {'pageNo': 1, 'pageSize': 100})
    assert result==VALID_RESPONSE

@pytest.mark.asyncio
async def test_get_records(api_instance, mocker):
    mocker.patch.object(api_instance, '_post_data_json', return_value = VALID_RESPONSE['data'])
    mocker.patch('soliscloud_api.soliscloud_api.SoliscloudAPI._prepare_header', return_value=VALID_HEADER)
    result=await api_instance._get_records("/TEST", KEY, SECRET, {'pageNo': 1, 'pageSize': 100})
    api_instance._post_data_json.assert_called_with('https://soliscloud_test.com:13333/TEST', VALID_HEADER, {'pageNo': 1, 'pageSize': 100})
    assert result==VALID_RESPONSE['data']['page']['records']

