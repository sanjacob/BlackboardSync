#!/usr/bin/env python3

"""BlackboardSync Controller."""

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

import sys
import webbrowser
from typing import Optional

from PyQt5.QtGui import QWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QSystemTrayIcon, QWidget

from .sync import BlackboardSync
from .institutions import Institution, get_names, InstitutionLogin
from .__about__ import __title__, __version__
from .updates import check_for_updates
from .qt.qt_elements import (LoginWebView, SyncTrayIcon, SettingsWindow,
                             RedownloadDialog, OSUtils, SetupWizard, UpdateFoundDialog)


class BBSyncController:
    """Connects an instance of BlackboardSync with the UI module."""

    def __init__(self):
        """Create an instance of the BlackboardSync Desktop App."""
        # Create model, which will try to retrieve existing configuration
        # If unsuccessful, we bring up login page
        self.model = BlackboardSync()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(__title__)
        self.app.setApplicationVersion(__version__)

        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self._init_ui()

        if self.model.university is None:
            OSUtils.add_to_startup()
            self._show_setup_window()
        else:
            self._build_login_window(self.model.university.login)
            self._show_login_window()
        self.app.exec()

    def _init_ui(self) -> None:
        self.setup_window = SetupWizard(get_names())
        self.setup_window.accepted.connect(self._setup_complete)

        self.login_window : Optional[LoginWebView] = None

        self.config_window = SettingsWindow()

        self.config_window.log_out_signal.connect(self._log_out)
        self.config_window.setup_wiz_signal.connect(self._reset_setup)
        self.config_window.save_signal.connect(self._save_setting_changes)

        self.tray = SyncTrayIcon()
        self.tray.quit_signal.connect(self._stop)
        self.tray.login_signal.connect(self._show_login_window)
        self.tray.settings_signal.connect(self._show_config_window)
        self.tray.reset_setup_signal.connect(self._reset_setup)
        self.tray.sync_signal.connect(self._force_sync)
        self.tray.activated.connect(self._tray_icon_activated)
        self.tray.open_dir_signal.connect(self._open_download_dir)
        self.tray.show_menu_signal.connect(self._update_tray_menu)

        self.app.setQuitOnLastWindowClosed(False)

    def _setup_complete(self) -> None:
        self.setup_window.setVisible(False)
        self.model.setup(self.setup_window.institution_index,
                         self.setup_window.download_location,
                         self.setup_window.min_year)
        self._build_login_window(self.model.university.login)
        self._show_login_window()

    def _build_login_window(self, uni_login_info: InstitutionLogin) -> None:
        # Get login url from uni DB
        self.login_window = LoginWebView(start_url=str(uni_login_info.start_url),
                                         target_url=str(uni_login_info.target_url))
        self.login_window.login_complete_signal.connect(self._login_complete)

    def _login_complete(self) -> None:
        if self.login_window is None:
            return

        self.app.setOverrideCursor(Qt.WaitCursor)
        # Call login function on sync
        auth = self.model.auth(self.login_window.cookie_jar)
        self.tray.set_logged_in(auth)
        self.login_window.setVisible(False)
        self.app.restoreOverrideCursor()
        self._check_for_updates()
        self.tray.show_msg('The download has started', 'BlackboardSync is running in the background. Find it in the system tray.')

    def _reset_setup(self) -> None:
        # Hide login window and show setup wizard
        if self.login_window is not None:
            self._log_out()
            self.login_window.setVisible(False)
        self._show_setup_window()

    def _check_for_updates(self) -> None:
        if (html_url := check_for_updates()) is not None:
            if UpdateFoundDialog().should_update:
                webbrowser.open(html_url)

    def _show_login_window(self) -> None:
        if self.login_window is not None:
            self._show_window(self.login_window)

    def _show_setup_window(self) -> None:
        self._show_window(self.setup_window)

    def _show_config_window(self) -> None:
        # Update displayed settings
        self.config_window.download_location = self.model.download_location
        self.config_window.username = self.model.username.split(':')[1]
        self.config_window.sync_frequency = self.model.sync_interval
        self._show_window(self.config_window)

    def _show_window(self, window: QWidget) -> None:
        window.setWindowState(Qt.WindowNoState)
        window.show()
        window.setFocus()

    def _open_download_dir(self) -> None:
        # Open folder in browser
        OSUtils.open_dir_in_file_browser(self.model.download_location)

    def _tray_icon_activated(self, activation_reason: QSystemTrayIcon.ActivationReason) -> None:
        if activation_reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.model.university is None:
                self._show_setup_window()
            # if not logged in
            elif not self.model.is_logged_in:
                self._show_login_window()

    def _log_out(self) -> None:
        if self.model.is_active:
            self.model.stop_sync()

        self.model.log_out()
        self.tray.set_logged_in(False)
        
        if self.login_window is not None:
            self.login_window.restore()
            self.login_window.setVisible(True)

        self.config_window.setVisible(False)

    def _save_setting_changes(self) -> None:
        self.config_window.setVisible(False)

        if self.model.download_location != self.config_window.download_location:
            redownload = RedownloadDialog().redownload
            self.model.change_download_location(self.config_window.download_location, redownload)

        self.model.sync_interval = self.config_window.sync_frequency

    def _force_sync(self) -> None:
        self.model.force_sync()

    def _update_tray_menu(self) -> None:
        # Update last sync time
        last_sync = self.model.last_sync_time
        last_sync_str = "Never"

        if last_sync is not None:
            last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")

        self.tray.update_last_synced(last_sync_str)
        self.tray.set_logged_in(self.model.is_logged_in)
        if self.login_window is not None:
            self.login_window.setVisible(not self.model.is_logged_in)

        # Disable button if currently syncing
        self.tray.toggle_currently_syncing(self.model.is_syncing)

    def _stop(self) -> None:
        if self.model.is_active:
            self.model.stop_sync()
        self.app.quit()


if __name__ == '__main__':
    controller = BBSyncController()
