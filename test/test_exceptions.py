import pytest
import soliscloud_api.soliscloud_api as api
from datetime import datetime


@pytest.fixture
def api_instance():
    instance = api.SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance


def test_soliscloud_error(mocker):
    err = api.SoliscloudAPI.SolisCloudError()
    assert f"{err}"=='SolisCloud API error'
    err = api.SoliscloudAPI.SolisCloudError("TEST")
    assert f"{err}"=='TEST'

    
def test_api_error(mocker):
    err = api.SoliscloudAPI.ApiError()
    assert f"{err}"=='API returned an error: Undefined API error occurred, error code: Unknown, response: None'
    err = api.SoliscloudAPI.ApiError("TEST")
    assert f"{err}"=='API returned an error: TEST, error code: Unknown, response: None'
    err = api.SoliscloudAPI.ApiError("TEST", 3, 1)
    assert f"{err}"=='API returned an error: TEST, error code: 3, response: 1'


def test_http_error(mocker):
    err = api.SoliscloudAPI.HttpError(408)
    now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
    assert f"{err}"==f'Your system time is different from server time, your time is {now}'
    err = api.SoliscloudAPI.HttpError(502)
    assert f"{err}"=='Http status code: 502'
    err = api.SoliscloudAPI.HttpError(502, "TEST")
    assert f"{err}"=='TEST'

    
def test_timeout_error(mocker):
    err = api.SoliscloudAPI.TimeoutError()
    assert f"{err}"==f'Timeout error occurred'
    err = api.SoliscloudAPI.TimeoutError("TEST")
    assert f"{err}"=='TEST'


