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

import pytest

from blackboard_sync.sync import BlackboardSync


class TestBlackboardSync:

    def test_sync(self, tmp_path):
        # Overwrite default values

        # Configuration filename is static
        BlackboardSync._config_filename = 'bbsync_test_config'

        # Create object
        sync = BlackboardSync()

        # Set sync folder to fixture
        sync._sync_folder = tmp_path
        sync._last_sync = ...
