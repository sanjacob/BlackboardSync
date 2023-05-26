"""BlackboardSync Graphical Interface Tests"""

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
from PyQt5 import QtCore
from PyQt5.Qt import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox

from blackboard_sync.qt import SyncPeriod, SettingsWindow



class TestSettingsWindow:
    user = 'exampleUser'
    data_source = 'exampleDataSource'

    def test_settings_window_initial_state(self, qtbot):
        settings_window = SettingsWindow()
        settings_window.show()
        qtbot.addWidget(settings_window)
        assert settings_window.sync_frequency == SyncPeriod.HALF_HOUR
        assert settings_window.download_location_hint.text() == 'Location to be shown here'

