"""
BlackboardSync Qt GUI
"""

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

from enum import IntEnum
from pathlib import Path
from typing import Optional

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QMenu,
                             QAction, QSystemTrayIcon, QStyle, QFileDialog, QMessageBox)


class SyncPeriod(IntEnum):
    """Enum containing all valid Sync intervals for this UI."""
    HALF_HOUR = 60 * 30
    ONE_HOUR = 60 * 60
    SIX_HOURS = 60 * 60 * 6


class AssetPath:
    """Helper class to get the path of app assets."""

    @staticmethod
    def get_qt_asset(asset_file: str) -> Path:
        return (Path(__file__).parent / f"{asset_file}.ui").resolve()

    @staticmethod
    def get_asset(icon: str) -> str:
        return str((Path(__file__).parent.parent / 'assets' / icon).resolve())

    @classmethod
    @property
    def app_logo(cls) -> QIcon:
        return QIcon(cls.get_asset("logo.png"))


class SyncTrayMenu(QMenu):
    """QMenu associated with app system tray icon."""
    _unauthenticated_status = "You haven't logged in"

    def __init__(self, logged_in: bool = False, last_synced: str = ""):
        super().__init__()
        self._last_synced = ""

        self._init_ui()
        self.update_last_synced(last_synced)
        self.set_logged_in(logged_in)

    def _init_ui(self) -> None:
        sync_icon = QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        close_icon = QApplication.style().standardIcon(QStyle.SP_DialogCloseButton)

        self.refresh = QAction("Sync now")
        self.refresh.setIcon(sync_icon)
        self.addAction(self.refresh)

        self.preferences = QAction("Preferences")
        self.addAction(self.preferences)

        self.addSeparator()

        self._status = QAction(self._unauthenticated_status)
        self._status.setEnabled(False)
        self.addAction(self._status)

        self.log_in = QAction("Log In")
        self.addAction(self.log_in)

        self.quit = QAction("Quit")
        self.quit.setIcon(close_icon)
        self.addAction(self.quit)

    def set_logged_in(self, logged: bool) -> None:
        self.refresh.setVisible(logged)
        self.preferences.setVisible(logged)
        self.log_in.setVisible(not logged)

        if logged:
            self._status.setText(f"Last Synced: {self._last_synced}")
        else:
            self._status.setText("Not Logged In")

    def update_last_synced(self, last: str) -> None:
        self._last_synced = last
        self._status.setText(f"Last Synced: {self._last_synced}")

    def toggle_currently_syncing(self, syncing: bool) -> None:
        self.refresh.setEnabled(not syncing)

        if syncing:
            self._status.setText("Syncing...")


class SyncTrayIcon(QSystemTrayIcon):
    """BlackboardSync system tray icon."""

    _tooltip = "Blackboard Sync"
    _sync_signal = pyqtSignal()
    _login_signal = pyqtSignal()
    _settings_signal = pyqtSignal()
    _quit_signal = pyqtSignal()
    _show_menu_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        # Create the icon
        icon = AssetPath.app_logo

        # Create the tray
        self.setIcon(icon)
        self.setVisible(True)

        # Create the menu
        self._menu = SyncTrayMenu()

        self._sync_signal = self._menu.refresh.triggered
        self._login_signal = self._menu.log_in.triggered
        self._settings_signal = self._menu.preferences.triggered
        self._quit_signal = self._menu.quit.triggered
        self._show_menu_signal = self._menu.aboutToShow

        # Add the menu to the tray
        self.setContextMenu(self._menu)
        self.setToolTip(self._tooltip)

    def set_logged_in(self, logged: bool) -> None:
        self._menu.set_logged_in(logged)

    def update_last_synced(self, last: str) -> None:
        self._menu.update_last_synced(last)

    def toggle_currently_syncing(self, syncing: bool) -> None:
        self._menu.toggle_currently_syncing(syncing)

    @property
    def sync_signal(self):
        return self._sync_signal

    @property
    def login_signal(self):
        return self._login_signal

    @property
    def settings_signal(self):
        return self._settings_signal

    @property
    def quit_signal(self):
        return self._quit_signal

    @property
    def show_menu_signal(self):
        return self._show_menu_signal


class RedownloadDialog(QMessageBox):
    """QMessageBox to show when asking whether files should be re-downloaded
    after a change in the sync location."""

    _window_title = "Redownload all files?"
    _dialog_text = "Should BlackboardSync redownload all files to the new location?"
    _info_text = "Answer no if you intend to move all past downloads manually (Recommended)"

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self.setText(self._dialog_text)
        self.setInformativeText(self._info_text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.setWindowTitle(self._window_title)
        self.setIcon(QMessageBox.Question)
        self.setWindowIcon(AssetPath.app_logo)

    @property
    def redownload(self) -> bool:
        return self.exec() == QMessageBox.Yes


class PersistenceWarning(QDialog):
    """QDialog shown if user chooses to store their
    login details on their device."""

    _window_title = "Do you wish to stay logged in?"

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        uic.loadUi(AssetPath.get_qt_asset(__class__.__name__), self)
        self.setWindowTitle(self._window_title)


class SettingsWindow(QWidget):
    """Settings windown UI element."""

    _window_title = "Settings"
    _initial_position = (300, 300)
    _log_out_signal = pyqtSignal()
    _save_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        uic.loadUi(AssetPath.get_qt_asset(__class__.__name__), self)

        self.move(*self._initial_position)
        self.setWindowTitle(self._window_title)

        self.select_download_location.clicked.connect(self._choose_location)
        self._log_out_signal = self.log_out_button.clicked
        self._save_signal = self.button_box.accepted

    def _choose_location(self) -> None:
        if (location := self._file_chooser_dialog()):
            self.download_location = location

    def _file_chooser_dialog(self) -> Optional[Path]:
        self.file_chooser = QFileDialog()
        self.file_chooser.setFileMode(QFileDialog.Directory)

        if self.file_chooser.exec():
            new_location = self.file_chooser.directory()
            return Path(new_location.path())

        return None

    @property
    def download_location(self) -> Path:
        return self._download_location

    @download_location.setter
    def download_location(self, location: Path) -> None:
        self._download_location = location.resolve()
        self.download_location_hint.setText(str(self._download_location))

    @property
    def data_source(self) -> str:
        return self.data_source_edit.text()

    @data_source.setter
    def data_source(self, data_source: str) -> None:
        self.data_source_edit.setText(data_source)

    @property
    def sync_frequency(self) -> int:
        return int([*SyncPeriod][self.frequency_combo.currentIndex()])

    @sync_frequency.setter
    def sync_frequency(self, f: int) -> None:
        self.frequency_combo.setCurrentIndex([*SyncPeriod].index(SyncPeriod(f)))

    @property
    def username(self) -> str:
        return self.current_session_label.text()

    @username.setter
    def username(self, username: str) -> None:
        if username:
            self.current_session_label.setText(f"Logged in as {username}")
        else:
            self.current_session_label.setText("Not currently logged in")

    @property
    def log_out_signal(self):
        return self._log_out_signal

    @property
    def save_signal(self):
        return self._save_signal


class LoginWindow(QWidget):
    """Login window UI element."""

    _window_title = "Log in to your blackboard account"
    _initial_position = (300, 300)
    _login_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        uic.loadUi(AssetPath.get_qt_asset(__class__.__name__), self)

        self.move(*self._initial_position)
        self.setWindowTitle(self._window_title)

        # Show warning if trying to select stay logged in option (until we find better option)
        # self._persistence_warn = PersistenceWarning()
        # self._persistence_warn.rejected.connect(self.stay_logged.toggle)
        # self.stay_logged.clicked.connect(self._show_warning)

        self.error_label.setVisible(False)
        self.login_button.clicked.connect(self.toggle_failed_login, True)

        self._login_signal = self.login_button.clicked

    def _show_warning(self) -> None:
        if self.stay_logged_checkbox:
            self._persistence_warn.show()

    def toggle_failed_login(self, visible: bool) -> None:
        self.error_label.setVisible(visible)

    @property
    def username(self) -> str:
        return self.user_edit.text()

    @property
    def password(self) -> str:
        return self.pass_edit.text()

    def clear_password(self) -> None:
        self.pass_edit.setText("")

    @property
    def stay_logged_checkbox(self) -> bool:
        return self.stay_logged.isChecked()

    @property
    def login_signal(self):
        return self._login_signal
