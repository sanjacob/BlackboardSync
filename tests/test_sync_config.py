"""BlackboardSync Configuration Manager Tests"""

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

import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st

from blackboard_sync.config import SyncConfig


def test_config_default_values():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        s = SyncConfig(tmp_path)
        assert s.last_sync_time is None

@given(st.datetimes())
def test_config_last_sync_time(sync_time):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config = SyncConfig(tmp_path)
        config.last_sync_time = sync_time
        assert config.last_sync_time == sync_time

        new_config = SyncConfig(tmp_path)
        assert new_config.last_sync_time == sync_time

