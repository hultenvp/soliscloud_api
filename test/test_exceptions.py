import pytest
from soliscloud_api import SoliscloudAPI
from soliscloud_api import (
    SoliscloudError,
    SoliscloudApiError,
    SoliscloudHttpError,
    SoliscloudTimeoutError,
)
from datetime import datetime


@pytest.fixture
def api_instance():
    instance = SoliscloudAPI('https://soliscloud_test.com:13333/', 1)
    return instance


def test_soliscloud_error(mocker):
    err = SoliscloudError()
    assert f"{err}" == ''
    err = SoliscloudError("TEST")
    assert f"{err}" == 'TEST'


def test_api_error(mocker):
    err = SoliscloudApiError()
    assert f"{err}" == 'API returned an error: Undefined API error occurred, error code: Unknown, response: None'  # noqa: E501
    err = SoliscloudApiError("TEST")
    assert f"{err}" == 'API returned an error: TEST, error code: Unknown, response: None'  # noqa: E501
    err = SoliscloudApiError("TEST", 3, 1)
    assert f"{err}" == 'API returned an error: TEST, error code: 3, response: 1'  # noqa: E501


def test_http_error(mocker):
    err = SoliscloudHttpError(408)
    now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
    assert f"{err}" == f'Your system time is different from server time, your time is {now}'  # noqa: E501
    err = SoliscloudHttpError(502)
    assert f"{err}" == 'Http status code: 502'
    err = SoliscloudHttpError(502, "TEST")
    assert f"{err}" == 'TEST'


def test_timeout_error(mocker):
    err = SoliscloudTimeoutError()
    assert f"{err}" == 'Timeout error occurred'
    err = SoliscloudTimeoutError("TEST")
    assert f"{err}" == 'TEST'
