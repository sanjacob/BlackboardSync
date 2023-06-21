"""BlackboardSync Tests"""

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

import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, ANY

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from hypothesis import provisional as pr

from blackboard_sync.blackboard.api import BlackboardSession
from blackboard_sync.download import BlackboardDownload
from blackboard_sync.blackboard.blackboard import BBMembership, BBCourse


@pytest.fixture
def mock_course():
    mock = Mock(spec=BBCourse)
    mock.code = 'TEST_BBC_CODE'
    mock.title = 'TEST_BBC_TITLE'
    mock.id = 'TEST_BBC_ID'
    return mock

@pytest.fixture
def mock_membership(mock_course):
    mock = Mock(spec=BBMembership)
    mock.courseId = mock_course.id
    return mock

@pytest.fixture
def mock_session(mock_membership, mock_course):
    mock = Mock(spec=BlackboardSession)
    mock.username = "example"
    mock.fetch_user_memberships.return_value = [ mock_membership ]
    mock.fetch_courses.return_value = mock_course
    return mock


@patch('blackboard_sync.download.platform')
@given(url=pr.urls(), current_platform=st.sampled_from(['Windows', 'Darwin']))
def test_create_link_windows_darwin(url, current_platform, mock_platform):
    mock_session = Mock(spec=BlackboardSession)
    mock_session.username = 'example'

    # Patch platform value so it can run independently of current OS.
    mock_platform.system.return_value = current_platform

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        link_path = Path(tmp_path / "link")
        real_path = link_path.with_suffix('.url')
        assert not real_path.exists()

        download = BlackboardDownload(mock_session, tmp_path)
        download._create_desktop_link(link_path, url)
        assert real_path.exists()
        contents = f"[InternetShortcut]\nURL={url}"

        with real_path.open('r') as link_file:
            assert link_file.read() == contents

@patch('blackboard_sync.download.platform')
@given(url=pr.urls(), current_platform=st.sampled_from(['Linux', '']))
def test_create_link_default(url, current_platform, mock_platform):
    mock_session = Mock(spec=BlackboardSession)
    mock_session.username = 'example'

    # Patch platform value so it can run independently of current OS.
    mock_platform.system.return_value = current_platform

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        link_path = Path(tmp_path / "link")
        assert not link_path.exists()

        download = BlackboardDownload(mock_session, tmp_path)
        download._create_desktop_link(link_path, url)
        assert link_path.exists()

        contents = f"[Desktop Entry]\nIcon=text-html\nType=Link\nURL[$e]={url}"

        with link_path.open('r') as link_file:
            assert link_file.read() == contents

def test_download_location(mock_session, tmp_path):
    download = BlackboardDownload(mock_session, tmp_path)
    assert download.download_location == tmp_path
    assert tmp_path.exists()

def test_logger(mock_session, tmp_path):
    download = BlackboardDownload(mock_session, tmp_path)
    assert isinstance(download.logger, logging.Logger)

def test_download_method_call_fetch_user_memberships_with_username(mock_session, tmp_path):
    expected_user = "test_username"
    mock_session.fetch_user_memberships.return_value = []
    mock_session.username = expected_user
    download = BlackboardDownload(mock_session, tmp_path)
    download.download()
    mock_session.fetch_user_memberships.assert_called_once_with(user_id=expected_user)

def test_download_method_call_fetch_courses_skip_private(mock_session, tmp_path):
    expected_course_id = 'TEST_BBC_ID'
    mock_session.fetch_courses.side_effect = ValueError('Private course')
    download = BlackboardDownload(mock_session, tmp_path)
    download.download()
    mock_session.fetch_courses.assert_called_once_with(course_id=expected_course_id)

def test_download_method_call_fetch_courses_raise_error(mock_session, tmp_path):
    mock_session.fetch_courses.side_effect = ValueError('Other error')
    download = BlackboardDownload(mock_session, tmp_path)
    with pytest.raises(ValueError) as excinfo:
        download.download()
    assert str(excinfo.value) == 'Other error'

def test_download_method_call_fetch_contents_with_id(mock_session, tmp_path):
    mock_session.fetch_contents.return_value = []
    download = BlackboardDownload(mock_session, tmp_path)
    download.download()
    mock_session.fetch_contents.assert_called_once_with(course_id='TEST_BBC_ID')
