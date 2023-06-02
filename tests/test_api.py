#!/usr/bin/env python3

"""BlackboardSync API Tests"""

# Copyright (C) 2021, Jacob Sánchez Pérez

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pytest
import requests

from blackboard_sync.blackboard.api import SafeFormat, BlackboardSession

# SafeFormat

def test_missing():
    safe_dict = SafeFormat({'a': 1})
    assert safe_dict['b'] == ''

def test_present():
    safe_dict = SafeFormat({'a': 1})
    assert safe_dict['a'] == 1


# BlackboardSession

@pytest.fixture
def mock_bbsession(mocker):
    """Fixture for the MockBlackboardSession class."""
    class MockBlackboardSession:
        _base_url = 'https://api.example.com'
        _timeout = 1
        # Logger
        logger = mocker.Mock()
        # Requests mocks
        response_mock = mocker.Mock()
        response_mock.json.return_value = {}

        session_mock = mocker.Mock()
        session_mock.get.return_value = response_mock
        _bb_session = session_mock

        def __init__(self, return_value):
            self.response_mock.json.return_value = return_value

        @BlackboardSession.get('/test_endpoint/{optional_id}')
        def api_operation(self, response):
            return response

    return MockBlackboardSession


@pytest.mark.parametrize("expected_error, response_data", [
    ('Server response empty', {}),
    ('Not authorized', {'status': 401, 'message': 'Error message'}),
    ('Private course', {'status': 403, 'message': 'Error message', 'code': 'bb-rest-course-is-private'}),
    ('Server responded with an error code', {'status': 418, 'message': 'Error message'})
])
def test_get_decorator_errors(mock_bbsession, expected_error, response_data):
    with pytest.raises(ValueError) as excinfo:
        mock_bbsession(response_data).api_operation()
    assert str(excinfo.value) == expected_error


@pytest.mark.parametrize("results", [
    {'a': 1, 'b': 2, 'c': 'd'},
])
def test_get_decorator_response(mock_bbsession, results):
    s = mock_bbsession(results)
    api_response = s.api_operation()
    assert api_response == results


@pytest.mark.parametrize("results", [
    [],
    [1, 2, 3],
    ['a', 'b', 'c']
])
def test_get_decorator_results(mock_bbsession, results):
    s = mock_bbsession({'results': results})
    api_response = s.api_operation()
    assert api_response == results


def test_get_decorator_endpoint(mock_bbsession, mocker):
    s = mock_bbsession({'results': []})
    api_response = s.api_operation()
    s.session_mock.get.assert_called_once_with('https://api.example.com/learn/api/public/v1/test_endpoint', timeout=mocker.ANY, params=mocker.ANY)


def test_get_decorator_endpoint_with_id(mock_bbsession, mocker):
    s = mock_bbsession({'results': []})
    api_response = s.api_operation(optional_id='test_id')
    s.session_mock.get.assert_called_once_with('https://api.example.com/learn/api/public/v1/test_endpoint/test_id', timeout=mocker.ANY, params=mocker.ANY)


def test_get_decorator_params(mock_bbsession, mocker):
    s = mock_bbsession({'results': []})
    expected = {'paramA': 1, 'paramB': 2, 'paramC': 'hello world'}
    api_response = s.api_operation(**expected)
    s.session_mock.get.assert_called_once_with(mocker.ANY, timeout=mocker.ANY, params=expected)


def test_get_decorator_params_with_endpoint_id(mock_bbsession, mocker):
    s = mock_bbsession({'results': []})
    expected = {'paramA': 1, 'paramB': 2, 'paramC': 'hello world', 'optional_id': 'passed'}
    # Even API endpoint are passed as parameters, which should not be an issue
    # but should be noted regardless (the server will simply ignore them)
    api_response = s.api_operation(**expected)
    s.session_mock.get.assert_called_once_with('https://api.example.com/learn/api/public/v1/test_endpoint/passed', timeout=mocker.ANY, params=expected)

# monkeypatch.setattr(requests, "Session", lambda *args, **kwargs: MockSession())
# s = BlackboardSession('base', None)
# s.fetch_announcements()
