import pytest
from soliscloud_api import SoliscloudAPI
from datetime import datetime


@pytest.fixture
def api_instance():
    instance = SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance


def test_soliscloud_error(mocker):
    err = SoliscloudAPI.SolisCloudError()
    assert f"{err}" == 'SolisCloud API error'
    err = SoliscloudAPI.SolisCloudError("TEST")
    assert f"{err}" == 'TEST'


def test_api_error(mocker):
    err = SoliscloudAPI.ApiError()
    assert f"{err}" == 'API returned an error: \
Undefined API error occurred, error code: Unknown, response: None'
    err = SoliscloudAPI.ApiError("TEST")
    assert f"{err}" == 'API returned an error: \
TEST, error code: Unknown, response: None'
    err = SoliscloudAPI.ApiError("TEST", 3, 1)
    assert f"{err}" == 'API returned an error: \
TEST, error code: 3, response: 1'


def test_http_error(mocker):
    err = SoliscloudAPI.HttpError(408)
    now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
    assert f"{err}" == f'Your system time is different from server time, \
your time is {now}'
    err = SoliscloudAPI.HttpError(502)
    assert f"{err}" == 'Http status code: 502'
    err = SoliscloudAPI.HttpError(502, "TEST")
    assert f"{err}" == 'TEST'


def test_timeout_error(mocker):
    err = SoliscloudAPI.TimeoutError()
    assert f"{err}" == 'Timeout error occurred'
    err = SoliscloudAPI.TimeoutError("TEST")
    assert f"{err}" == 'TEST'
