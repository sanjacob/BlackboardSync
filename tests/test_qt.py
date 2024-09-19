"""Graphical Interface Tests"""

# Copyright (C) 2024, Jacob Sánchez Pérez

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.


import pytest
import requests
from datetime import datetime, timezone

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QDialogButtonBox

from blackboard_sync.qt import (
    SetupWizard,
    LoginWebView,
    SettingsWindow,
    SyncTrayIcon,
)

from blackboard_sync.qt.dialogs import DirDialog, Dialogs


@pytest.fixture
def settings_window():
    window = SettingsWindow()
    window.show()
    return window


@pytest.fixture
def tray_icon():
    return SyncTrayIcon()


@pytest.fixture
def make_setup_wizard(monkeypatch):
    def _make_setup_wizard(institutions: list[str]):
        wizard = SetupWizard("", institutions)

        # Don't show uni not supported dialog
        monkeypatch.setattr(Dialogs, "uni_not_supported_dialog", lambda *args: True)

        # Don't show file chooser dialog
        monkeypatch.setattr(QFileDialog, "exec", lambda *args: True)
        monkeypatch.setattr(QFileDialog, "directory", lambda *args: "/")

        # monkeypatch.setattr(wizard, "_", lambda *args: None)
        return wizard

    return _make_setup_wizard


class TestSetupWizard:
    intro = 'You are a few steps away from syncing your Blackboard Learn content straight to your device!'
    uni_selection = 'First, tell us where you study'
    location_selection = 'Where do you want files to be downloaded?'
    page_number = 4
    institutions = ['Never', 'Gonna', 'Give', 'You', 'Up']

    def test_wizard_page_number(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard([])
        qtbot.addWidget(wizard)
        assert len(wizard.pageIds()) == self.page_number

    def test_wizard_intro_label(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard([])
        qtbot.addWidget(wizard)
        assert wizard.intro_label.text() == self.intro

    def test_wizard_uni_selection_label(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard([])
        qtbot.addWidget(wizard)
        assert wizard.uni_selection_label.text() == self.uni_selection

    def test_wizard_sync_location_label(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard([])
        qtbot.addWidget(wizard)
        assert wizard.sync_location_label.text() == self.location_selection

    def test_wizard_institutions(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard(self.institutions)
        qtbot.addWidget(wizard)

        for i in range(wizard.uni_selection_box.count()):
            assert wizard.uni_selection_box.itemText(i) == self.institutions[i]

    def test_wizard_page_one(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard(self.institutions)
        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)
        assert wizard.currentId() == SetupWizard.Pages.INTRO

    def test_wizard_page_two(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard(self.institutions)
        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)
        wizard.next()
        assert wizard.currentId() == SetupWizard.Pages.INSTITUTION

    def test_wizard_valid_institution(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard(self.institutions)
        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)
        wizard.next()
        qtbot.keyClicks(wizard.uni_selection_box, self.institutions[2])
        qtbot.keyClick(wizard.uni_selection_box, Qt.Key.Key_Enter)
        assert wizard.currentId() == SetupWizard.Pages.DOWNLOAD_LOCATION

    def test_wizard_invalid_institution_enter(self, qtbot, make_setup_wizard, monkeypatch):
        wizard = make_setup_wizard(self.institutions)

        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)

        wizard.next()
        qtbot.keyClicks(wizard.uni_selection_box, 'Fake')
        qtbot.keyClick(wizard.uni_selection_box, Qt.Key.Key_Enter)
        assert wizard.currentId() == SetupWizard.Pages.INSTITUTION

    def test_wizard_invalid_institution(self, qtbot, make_setup_wizard, monkeypatch):
        wizard = make_setup_wizard(self.institutions)

        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)

        wizard.next()
        qtbot.keyClicks(wizard.uni_selection_box, 'Fake')
        wizard.next()
        assert wizard.currentId() == SetupWizard.Pages.INSTITUTION

    def test_wizard_institution_attribute(self, qtbot, make_setup_wizard):
        wizard = make_setup_wizard(self.institutions)
        # Necessary to get currentId
        wizard.show()
        qtbot.addWidget(wizard)
        wizard.next()
        qtbot.keyClicks(wizard.uni_selection_box, self.institutions[3])
        qtbot.keyClick(wizard.uni_selection_box, Qt.Key.Key_Enter)
        assert wizard.institution_index == 3


SyncPeriod = SettingsWindow.SyncPeriod

class TestSettingsWindow:
    user = 'exampleUser'
    data_source = 'exampleDataSource'

    def test_settings_window_initial_state(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        assert settings_window.sync_frequency == SyncPeriod.HALF_HOUR

    def test_settings_window_download_location_dialog(self, qtbot, settings_window,
                                                      tmp_path, monkeypatch):
        qtbot.addWidget(settings_window)

        monkeypatch.setattr(DirDialog, "choose", lambda *args: tmp_path)

        qtbot.mouseClick(settings_window.select_download_location, Qt.MouseButton.LeftButton)
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
        qtbot.mouseClick(settings_window.frequency_combo, Qt.MouseButton.LeftButton)
        qtbot.keyEvent(QTest.KeyAction.Click, settings_window.frequency_combo, Qt.Key.Key_Down)
        qtbot.keyEvent(QTest.KeyAction.Click, settings_window.frequency_combo, Qt.Key.Key_Enter)
        assert settings_window.sync_frequency == SyncPeriod.ONE_HOUR
        qtbot.mouseClick(settings_window.frequency_combo, Qt.MouseButton.LeftButton)
        qtbot.keyEvent(QTest.KeyAction.Click, settings_window.frequency_combo, Qt.Key.Key_Down)
        qtbot.keyEvent(QTest.KeyAction.Click, settings_window.frequency_combo, Qt.Key.Key_Enter)
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

        with qtbot.waitSignal(settings_window.signals.log_out) as blocker:
            qtbot.mouseClick(settings_window.log_out_button, Qt.MouseButton.LeftButton)

        assert blocker.signal_triggered
    
    def test_settings_window_setup_wizard_signal(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)

        with qtbot.waitSignal(settings_window.signals.setup_wiz) as blocker:
            qtbot.mouseClick(settings_window.setup_button, Qt.MouseButton.LeftButton)

        assert blocker.signal_triggered

    def test_settings_window_save_signal(self, qtbot, settings_window):
        qtbot.addWidget(settings_window)
        save_btn = settings_window.button_box.button(QDialogButtonBox.StandardButton.Save)

        with qtbot.waitSignal(settings_window.signals.save) as blocker:
            qtbot.mouseClick(save_btn, Qt.MouseButton.LeftButton)

        assert blocker.signal_triggered


class TestSyncTrayIcon:
    def test_tray_icon_initial_state(self, qtbot, tray_icon):
        assert tray_icon._menu._status.text() == 'Not logged in'
        assert not tray_icon._menu.refresh.isVisible()
        assert not tray_icon._menu.preferences.isVisible()
        assert tray_icon._menu._status.isVisible()
        assert tray_icon._menu.quit.isVisible()

    def test_tray_icon_logged_in_state(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        assert tray_icon._menu._status.text() != 'Not logged in'
        assert tray_icon._menu.refresh.isVisible()
        assert tray_icon._menu.refresh.isEnabled()
        assert tray_icon._menu.preferences.isVisible()
        assert tray_icon._menu._status.isVisible()
        assert tray_icon._menu.quit.isVisible()

    def test_tray_icon_currently_syncing(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        tray_icon.set_currently_syncing(True)
        assert tray_icon._menu._status.text() == 'Downloading now...'
        assert not tray_icon._menu.refresh.isEnabled()

        tray_icon.set_currently_syncing(False)
        assert tray_icon._menu.refresh.isEnabled()

    def test_tray_icon_setupwiz_signal(self, qtbot, tray_icon):
        with qtbot.waitSignal(tray_icon.signals.reset_setup) as blocker:
            tray_icon._menu.reset_setup.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_quit_signal(self, qtbot, tray_icon):
        with qtbot.waitSignal(tray_icon.signals.quit) as blocker:
            tray_icon._menu.quit.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_settings_signal(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        with qtbot.waitSignal(tray_icon.signals.settings) as blocker:
            tray_icon._menu.preferences.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_sync_signal(self, qtbot, tray_icon):
        tray_icon.set_logged_in(True)
        with qtbot.waitSignal(tray_icon.signals.force_sync) as blocker:
            tray_icon._menu.refresh.trigger()

        assert blocker.signal_triggered

    def test_tray_icon_last_synced(self, qtbot, tray_icon):
        exampleDate = datetime(year=1970, month=1, day=10, tzinfo=timezone.utc)
        tray_icon.set_last_synced(exampleDate)
        assert tray_icon._menu._last_synced == exampleDate
        assert '54 years' in tray_icon._menu._status.text()
