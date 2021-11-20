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
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialogButtonBox
from blackboard_sync.qt import (SettingsWindow, LoginWindow, SyncTrayIcon, SyncPeriod)


@pytest.fixture
def login_window():
    window = LoginWindow()
    window.show()
    return window


@pytest.fixture
def settings_window():
    window = SettingsWindow()
    window.show()
    return window


@pytest.fixture
def tray_icon():
    icon = SyncTrayIcon()
    return icon


class TestLoginWindow:
    user = 'exampleUser'
    password = 'examplePassword'

    def test_login_window_initial_state(self, qtbot, login_window):
        qtbot.addWidget(login_window)
        assert not login_window.error_label.isVisible()
        assert login_window.username == ''
        assert login_window.password == ''
        assert not login_window.stay_logged_checkbox

    @pytest.mark.parametrize('visibility', [True, False])
    def test_login_window_error_label(self, qtbot, login_window, visibility):
        qtbot.addWidget(login_window)
        login_window.toggle_failed_login(visibility)
        assert login_window.error_label.isVisible() == visibility

    def test_login_window_input_boxes(self, qtbot, login_window):
        qtbot.addWidget(login_window)
        qtbot.keyClicks(login_window.user_edit, self.user)
        qtbot.keyClicks(login_window.pass_edit, self.password)
        assert login_window.username == self.user
        assert login_window.password == self.password

    def test_login_window_clear_pass(self, qtbot, login_window):
        qtbot.addWidget(login_window)
        qtbot.keyClicks(login_window.pass_edit, self.password)
        assert login_window.password == self.password
        login_window.clear_password()
        assert login_window.password == ''

    def test_login_window_checkbox(self, qtbot, login_window):
        qtbot.addWidget(login_window)
        checkbox_pos = QtCore.QPoint(login_window.stay_logged.width() // 5,
                                     login_window.stay_logged.height() // 2)
        qtbot.mouseClick(login_window.stay_logged, QtCore.Qt.LeftButton, pos=checkbox_pos)
        assert login_window.stay_logged_checkbox

        qtbot.mouseClick(login_window.stay_logged, QtCore.Qt.LeftButton, pos=checkbox_pos)
        assert not login_window.stay_logged_checkbox

    def test_login_window_signal(self, qtbot, login_window):
        qtbot.addWidget(login_window)
        qtbot.keyClicks(login_window.user_edit, self.user)
        qtbot.keyClicks(login_window.pass_edit, self.password)

        with qtbot.waitSignal(login_window.login_signal) as blocker:
            qtbot.mouseClick(login_window.login_button, QtCore.Qt.LeftButton)

        assert blocker.signal_triggered


class TestSettingsWindow:
    user = 'exampleUser'
    data_source = 'exampleDataSource'

    def test_settings_window_initial_state(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        assert settings_window.sync_frequency == SyncPeriod.HALF_HOUR
        assert settings_window.download_location_hint.text() == 'Location to be shown here'

    def test_settings_window_download_location_dialog(self, qtbot, settings_window,
                                                      tmp_path, monkeypatch):
        qtbot.addWidget(settings_window)

        monkeypatch.setattr(
            settings_window, "_file_chooser_dialog", lambda *args: tmp_path
        )

        qtbot.mouseClick(settings_window.select_download_location, QtCore.Qt.LeftButton)
        assert settings_window.download_location == tmp_path
        assert settings_window.download_location_hint.text() == str(tmp_path)

    def test_settings_window_download_location(self, qtbot, settings_window, tmp_path):
        qtbot.addWidget(settings_window)
        settings_window.download_location = tmp_path
        assert settings_window.download_location_hint.text() == str(tmp_path)
        assert settings_window.download_location == tmp_path

    def test_settings_window_sync_frequency(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        settings_window.sync_frequency = int(SyncPeriod.HALF_HOUR)
        assert settings_window.sync_frequency == SyncPeriod.HALF_HOUR

        settings_window.sync_frequency = int(SyncPeriod.ONE_HOUR)
        assert settings_window.sync_frequency == SyncPeriod.ONE_HOUR

        settings_window.sync_frequency = int(SyncPeriod.SIX_HOURS)
        assert settings_window.sync_frequency == SyncPeriod.SIX_HOURS

    def test_settings_window_sync_frequency_keys(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)

        assert settings_window.sync_frequency == SyncPeriod.HALF_HOUR
        qtbot.mouseClick(settings_window.frequency_combo, QtCore.Qt.LeftButton)
        qtbot.keyEvent(QTest.Click, settings_window.frequency_combo, QtCore.Qt.Key_Down)
        qtbot.keyEvent(QTest.Click, settings_window.frequency_combo, QtCore.Qt.Key_Enter)
        assert settings_window.sync_frequency == SyncPeriod.ONE_HOUR
        qtbot.mouseClick(settings_window.frequency_combo, QtCore.Qt.LeftButton)
        qtbot.keyEvent(QTest.Click, settings_window.frequency_combo, QtCore.Qt.Key_Down)
        qtbot.keyEvent(QTest.Click, settings_window.frequency_combo, QtCore.Qt.Key_Enter)
        assert settings_window.sync_frequency == SyncPeriod.SIX_HOURS

    def test_settings_window_data_source(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        settings_window.data_source = self.data_source
        assert settings_window.data_source == self.data_source

    def test_settings_window_username(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        settings_window.username = self.user
        assert self.user in settings_window.username

        settings_window.username = ''
        assert settings_window.username != ''
        assert self.user not in settings_window.username

    def test_settings_window_log_out_signal(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)

        with qtbot.waitSignal(settings_window.log_out_signal) as blocker:
            qtbot.mouseClick(settings_window.log_out_button, QtCore.Qt.LeftButton)

        assert blocker.signal_triggered

    def test_settings_window_save_signal(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)

        with qtbot.waitSignal(settings_window.save_signal) as blocker:
            qtbot.mouseClick(settings_window.button_box.button(QDialogButtonBox.Save),
                             QtCore.Qt.LeftButton)

        assert blocker.signal_triggered


class TestSyncTrayIcon:
    def test_tray_icon_initial_state(self, qtbot, tray_icon):
        assert tray_icon._menu._status.text() == 'Not Logged In'
        assert not tray_icon._menu.refresh.isVisible()
        assert not tray_icon._menu.preferences.isVisible()
        assert tray_icon._menu.log_in.isVisible()
        assert tray_icon._menu._status.isVisible()
        assert tray_icon._menu.quit.isVisible()

    def test_tray_icon_logged_in_state(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        assert tray_icon._menu._status.text() != 'Not Logged In'
        assert tray_icon._menu.refresh.isVisible()
        assert tray_icon._menu.refresh.isEnabled()
        assert tray_icon._menu.preferences.isVisible()
        assert not tray_icon._menu.log_in.isVisible()
        assert tray_icon._menu._status.isVisible()
        assert tray_icon._menu.quit.isVisible()

    def test_tray_icon_currently_syncing(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        tray_icon.toggle_currently_syncing(True)
        assert tray_icon._menu._status.text() == 'Syncing...'
        assert not tray_icon._menu.refresh.isEnabled()

        tray_icon.toggle_currently_syncing(False)
        assert tray_icon._menu.refresh.isEnabled()

    def test_tray_icon_login_signal(self, qtbot, tray_icon):
        with qtbot.waitSignal(tray_icon.login_signal) as blocker:
            tray_icon._menu.log_in.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_quit_signal(self, qtbot, tray_icon):
        with qtbot.waitSignal(tray_icon.quit_signal) as blocker:
            tray_icon._menu.quit.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_settings_signal(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        with qtbot.waitSignal(tray_icon.settings_signal) as blocker:
            tray_icon._menu.preferences.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_sync_signal(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        with qtbot.waitSignal(tray_icon.sync_signal) as blocker:
            tray_icon._menu.refresh.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_last_synced(self, qtbot, tray_icon):
        exampleDate = '1970-01-10'
        tray_icon.update_last_synced(exampleDate)
        assert tray_icon._menu._last_synced == exampleDate
        assert exampleDate in tray_icon._menu._status.text()
