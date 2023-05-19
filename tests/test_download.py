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
from unittest.mock import Mock, patch

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from hypothesis import provisional as pr

from blackboard_sync.blackboard.api import BlackboardSession
from blackboard_sync.download import BlackboardDownload


@pytest.fixture
def mock_session():
    mock = Mock(spec=BlackboardSession)
    mock.username = "example"
    return mock


class TestBlackboardDownload:
    @patch('blackboard_sync.download.platform')
    @given(url=pr.urls(), current_platform=st.sampled_from(['Windows', 'Darwin']))
    def test_create_link_windows_darwin(self, url, current_platform, mock_platform):
        mock_session = Mock(spec=BlackboardSession)
        mock_session.username = 'example'

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
    def test_create_link_default(self, url, current_platform, mock_platform):
        mock_session = Mock(spec=BlackboardSession)
        mock_session.username = 'example'

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

    def test_download_location(self, mock_session, tmp_path):
        download = BlackboardDownload(mock_session, tmp_path)
        assert download.download_location == tmp_path
        assert tmp_path.exists()

    def test_default_data_source(self, mock_session, tmp_path):
        download = BlackboardDownload(mock_session, tmp_path)
        assert download.data_source == '_21_1'

    def test_logger(self, mock_session, tmp_path):
        download = BlackboardDownload(mock_session, tmp_path)
        assert isinstance(download.logger, logging.Logger)
