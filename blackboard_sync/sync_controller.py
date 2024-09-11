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
from importlib.metadata import version, PackageNotFoundError

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QStyleFactory, QSystemTrayIcon, QWidget

from .sync import BlackboardSync
from .__about__ import __id__, __title__, __uri__
from .updates import check_for_updates
from .institutions import Institution, InstitutionLogin, get_names, autodetect
from .qt import LoginWebView, SetupWizard, SettingsWindow, SyncTrayIcon
from .qt.utils import add_to_startup, open_in_file_browser
from .qt.dialogs import RedownloadDialog, UpdateFoundDialog


class BBSyncController:
    """Connects an instance of BlackboardSync with the UI module."""

    tray_msg = {
        "container_update": ('Updates available', 'You can update BlackboardSync from the Software Center', 1, 4),
        "download_started": ('The download has started', 'BlackboardSync is running in the background. Find it in the system tray.'),
        "download_error": ('The download cannot be completed', 'There was an error validating your course content. Please report this issue.', 3, 10)
    }

    def __init__(self):
        """Create an instance of the BlackboardSync Desktop App."""
        # Create model, which will try to retrieve existing configuration
        # If unsuccessful, we bring up login page
        self.model = BlackboardSync()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(__title__)

        try:
            __version__ = version("blackboard_sync")
        except PackageNotFoundError:
            pass
        else:
            self.app.setApplicationVersion(__version__)

        self._init_ui()
        self._has_notified_error = False

        if self.model.university is None:
            add_to_startup(__id__)
            self._show_setup_window()
        else:
            self._build_login_window(self.model.university.login)
            self._show_login_window()
        self.app.exec()

    def _init_ui(self) -> None:
        self.setup_window = SetupWizard(__uri__, get_names(), autodetect())
        self.setup_window.accepted.connect(self._setup_complete)

        self.login_window : Optional[LoginWebView] = None

        self.config_window = SettingsWindow()

        self.config_window.signals.log_out.connect(self._log_out)
        self.config_window.signals.setup_wiz.connect(self._reset_setup)
        self.config_window.signals.save.connect(self._save_setting_changes)

        self.tray = SyncTrayIcon()
        self.tray.signals.quit.connect(self._stop)
        self.tray.signals.login.connect(self._show_login_window)
        self.tray.signals.settings.connect(self._show_config_window)
        self.tray.signals.reset_setup.connect(self._reset_setup)
        self.tray.signals.sync.connect(self._force_sync)
        self.tray.activated.connect(self._tray_icon_activated)
        self.tray.signals.open_dir.connect(self._open_download_dir)
        self.tray.signals.show_menu.connect(self._update_tray_menu)

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
        self.login_window.signals.login_complete.connect(self._login_complete)

    def _login_complete(self) -> None:
        if self.login_window is None:
            return

        self.app.setOverrideCursor(Qt.CursorShape.WaitCursor)
        # Call login function on sync
        auth = self.model.auth(self.login_window.cookie_jar)
        self.tray.set_logged_in(auth)
        self.login_window.setVisible(False)
        self.app.restoreOverrideCursor()
        self._check_for_updates()
        self.tray.notify(*(self.tray_msg["download_started"]))

    def _reset_setup(self) -> None:
        # Hide login window and show setup wizard
        if self.login_window is not None:
            self._log_out()
            self.login_window.setVisible(False)
        self._show_setup_window()

    def _check_for_updates(self) -> None:
        if (html_url := check_for_updates()) is not None:
            if html_url == 'container':
                self.tray.notify(*(self.tray_msg["container_update"]))
            elif UpdateFoundDialog().should_update:
                webbrowser.open(html_url)

    def _show_login_window(self) -> None:
        if self.login_window is not None:
            self._show_window(self.login_window)

    def _show_setup_window(self) -> None:
        self._show_window(self.setup_window)

    def _show_config_window(self) -> None:
        # Update displayed settings
        self.config_window.download_location = self.model.download_location
        self.config_window.username = self.model.username
        self.config_window.sync_frequency = self.model.sync_interval
        self._show_window(self.config_window)

    def _show_window(self, window: QWidget) -> None:
        window.setWindowState(Qt.WindowState.WindowNoState)
        window.show()
        window.setFocus()

    def _open_download_dir(self) -> None:
        # Open folder in browser
        open_in_file_browser(self.model.download_location)

    def _tray_icon_activated(self, activation_reason: QSystemTrayIcon.ActivationReason) -> None:
        if activation_reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.model.university is None:
                self._show_setup_window()
            # if not logged in
            elif not self.model.is_logged_in:
                self._show_login_window()
        if self.model.has_error and not self._has_notified_error:
            self.tray.notify(*(self.tray_msg["download_error"]))
            webbrowser.open("https://github.com/sanjacob/BlackboardSync/issues")
            self._has_notified_error = True

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
            self.model.download_location = self.config_window.download_location

            if redownload:
                self.model.redownload()

        self.model.sync_interval = self.config_window.sync_frequency

    def _force_sync(self) -> None:
        self.model.force_sync()

    def _update_tray_menu(self) -> None:
        # Update last sync time
        self.tray.set_last_synced(self.model.last_sync_time)
        self.tray.set_logged_in(self.model.is_logged_in)
        if self.login_window is not None:
            self.login_window.setVisible(not self.model.is_logged_in)

        # Disable button if currently syncing
        self.tray.set_currently_syncing(self.model.is_syncing)

    def _stop(self) -> None:
        if self.model.is_active:
            self.model.stop_sync()
        self.app.quit()


if __name__ == '__main__':
    controller = BBSyncController()
