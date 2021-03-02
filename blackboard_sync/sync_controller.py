#!/usr/bin/env python3

"""
BlackboardSync Controller
Copyright (C) 2020
Jacob Sánchez Pérez
"""

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
from sync import BlackboardSync
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QSystemTrayIcon
from qt.qt_elements import LoginWindow, SyncTrayIcon, SettingsWindow, RedownloadDialog

from __about__ import __title__, __version__


class BBSyncController:
    def __init__(self):
        # Create model, which will try to retrieve existing configuration
        # If unsuccessful, we bring up login page
        self.model = BlackboardSync()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(__title__)
        self.app.setApplicationVersion(__version__)

        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self._init_ui()

        if not self.model.is_logged_in:
            self._show_login_window()
        else:
            self.tray.set_logged_in(True)

        self.app.exec()

    def _init_ui(self):
        self.login_window = LoginWindow()
        self.login_window.login_signal.connect(self._attempt_login)

        self.config_window = SettingsWindow()

        self.config_window.log_out_signal.connect(self._log_out)
        self.config_window.save_signal.connect(self._save_setting_changes)

        self.tray = SyncTrayIcon()
        self.tray.quit_signal.connect(self._stop)
        self.tray.login_signal.connect(self._show_login_window)
        self.tray.settings_signal.connect(self._show_config_window)
        self.tray.sync_signal.connect(self._force_sync)
        self.tray.activated.connect(self._tray_icon_activated)
        self.tray.show_menu_signal.connect(self._update_tray_menu)

        self.app.setQuitOnLastWindowClosed(False)

    def _attempt_login(self):
        self.app.setOverrideCursor(Qt.WaitCursor)
        # Call login function on sync
        auth = self.model.auth(self.login_window.username, self.login_window.password,
                               self.login_window.stay_logged_checkbox)
        self.tray.set_logged_in(auth)
        self.login_window.toggle_failed_login(not auth)
        self.login_window.setVisible(not auth)

        if auth:
            self.login_window.clear_password()

        self.app.restoreOverrideCursor()

    def _show_login_window(self):
        self._show_window(self.login_window)

    def _show_config_window(self):
        # Update displayed settings
        self.config_window.download_location = self.model.sync_folder
        self.config_window.data_source = self.model.data_source
        self.config_window.username = self.model.username.split(':')[1]
        self._show_window(self.config_window)

    def _show_window(self, window):
        window.show()
        window.setWindowState(Qt.WindowNoState)

    def _tray_icon_activated(self, activation_reason: QSystemTrayIcon.ActivationReason):
        if activation_reason == QSystemTrayIcon.ActivationReason.Trigger:
            # if not logged in
            if not self.model.is_logged_in:
                self._show_login_window()
            else:
                # Open folder in browser
                self.model.open_sync_folder()

    def _log_out(self):
        self.model.log_out()
        self.tray.set_logged_in(False)
        self.login_window.setVisible(True)
        self.config_window.setVisible(False)

    def _save_setting_changes(self):
        self.config_window.setVisible(False)

        if self.model.sync_folder != self.config_window.download_location:
            redownload = RedownloadDialog().redownload
            self.model.set_sync_folder(self.config_window.download_location, redownload)

        self.model.data_source = self.config_window.data_source
        self.model.sync_period = self.config_window.sync_frequency

    def _force_sync(self):
        self.model.force_sync()

    def _update_tray_menu(self):
        # Update last sync time
        last_sync = self.model.last_sync
        last_sync_str = "Never"

        if last_sync is not None:
            last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")

        self.tray.update_last_synced(last_sync_str)
        self.tray.set_logged_in(self.model.is_logged_in)

        # Disable button if currently syncing
        self.tray.toggle_currently_syncing(self.model.is_syncing)

    def _stop(self):
        if self.model.sync_on:
            self.model.stop_sync()
        self.app.quit()


if __name__ == '__main__':
    controller = BBSyncController()
