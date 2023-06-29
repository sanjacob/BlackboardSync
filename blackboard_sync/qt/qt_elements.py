"""BlackboardSync Qt GUI."""

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

import os
import sys
import json
import platform
import subprocess
import webbrowser
from enum import IntEnum
from typing import Optional
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSettings, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWidgets import (QMenu, QStyle, QAction, QDialog, QWidget, QWizard,
                             QCompleter, QFileDialog, QMessageBox, QApplication,
                             QSystemTrayIcon, QComboBox, QLabel, QCheckBox, QSpinBox)
from requests.cookies import RequestsCookieJar
from PyQt5.QtWebEngineCore import QWebEngineCookieStore
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile


class SyncPeriod(IntEnum):
    """Enum containing all valid Sync intervals for this UI."""

    HALF_HOUR = 60 * 30
    ONE_HOUR = 60 * 60
    SIX_HOURS = 60 * 60 * 6


class Assets:
    """Helper class to get the path of app assets."""

    _icon_filename = 'logo.png'
    _watermark_filename = 'watermark.png'

    @staticmethod
    def _get_qt_asset_path(asset_file) -> Path:
        """Get the `Path` corresponding to a Qt UI file."""
        return (Path(__file__).parent / f"{asset_file}.ui").resolve()

    @classmethod
    def load_ui(cls, qt_obj):
        """Load a UI file for a `QObject`."""
        uic.loadUi(cls._get_qt_asset_path(qt_obj.__class__.__name__), qt_obj)

    @staticmethod
    def _get_asset_path(icon) -> Path:
        """Get the `Path` of a media asset."""
        return (Path(__file__).parent.parent / 'assets' / icon).resolve()

    @classmethod
    def icon(cls) -> QIcon:
        """`QIcon` of application logo."""
        return QIcon(str(cls._get_asset_path(cls._icon_filename)))

    @classmethod
    def watermark(cls) -> QPixmap:
        """`QPixmap` of application watermark."""
        wm = QPixmap(str(cls._get_asset_path(cls._watermark_filename)))
        wm = wm.scaledToWidth(100)
        return wm


class OSUtils:
    @staticmethod
    def open_dir_in_file_browser(dir_to_open: Path) -> None:
        """Start a subprocess to open the default file explorer at the given location."""
        if sys.platform == "win32":
            os.startfile(dir_to_open)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", dir_to_open])
        else:
            subprocess.Popen(["xdg-open", dir_to_open])

    @staticmethod
    def add_to_startup() -> None:
        """Add the app to start up on macOS."""
        if platform.system() != "Darwin":
            return

        # Set the paths and filenames
        app_path = '/Applications/BBSync.app'
        launch_dir = Path("~/Library/LaunchAgents").expanduser()

        if not launch_dir.exists():
            launch_dir.mkdir()

        plist_path = launch_dir / "app.bbsync.plist"
        plist_path.touch()

        # Create the QSettings object
        settings = QSettings(str(plist_path), QSettings.NativeFormat)

        # Set the launch agent properties
        settings.setValue('Label', 'app.bbsync.BBSync')
        settings.setValue('ProgramArguments', app_path)
        settings.setValue('RunAtLoad', True)
        settings.setValue('KeepAlive', False)

        # Save the settings to create the plist file
        settings.sync()


class SyncTrayMenu(QMenu):
    """`QMenu` associated with app system tray icon."""

    _unauthenticated_status = "You haven't logged in"

    def __init__(self, logged_in: bool = False, last_synced: str = ""):
        """Create the menu for a `SyncTrayIcon`.

        :param bool logged_in: Whether user is currently logged in.
        :param str last_synced: Last sync time shown.
        """
        super().__init__()
        self._last_synced = ""

        self._init_ui()
        self.update_last_synced(last_synced)
        self.set_logged_in(logged_in)

    def _init_ui(self) -> None:
        sync_icon = QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        close_icon = QApplication.style().standardIcon(QStyle.SP_DialogCloseButton)
        open_dir_icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)

        self.refresh = QAction("Sync now")
        self.refresh.setIcon(sync_icon)
        self.addAction(self.refresh)

        self.open_dir = QAction("Open downloads")
        self.open_dir.setIcon(open_dir_icon)
        self.addAction(self.open_dir)

        self.preferences = QAction("Preferences")
        self.addAction(self.preferences)

        self.addSeparator()

        self._status = QAction(self._unauthenticated_status)
        self._status.setEnabled(False)
        self.addAction(self._status)

        self.log_in = QAction("Log In")
        self.addAction(self.log_in)

        self.reset_setup = QAction("Redo Setup")
        self.addAction(self.reset_setup)

        self.quit = QAction("Quit")
        self.quit.setIcon(close_icon)
        self.addAction(self.quit)

    def set_logged_in(self, logged: bool) -> None:
        """Set the UI to reflect logged-in status."""
        self.refresh.setVisible(logged)
        self.preferences.setVisible(logged)
        self.reset_setup.setVisible(not logged)
        self.open_dir.setVisible(logged)
        self.log_in.setVisible(not logged)

        if logged:
            self._status.setText(f"Last Synced: {self._last_synced}")
        else:
            self._status.setText("Not Logged In")

    def update_last_synced(self, last: str) -> None:
        """Update the time of last download shown to user."""
        self._last_synced = last
        self._status.setText(f"Last Synced: {self._last_synced}")

    def toggle_currently_syncing(self, syncing: bool) -> None:
        """Toggle the currently syncing indicator."""
        self.refresh.setEnabled(not syncing)

        if syncing:
            self._status.setText("Downloading now...")


class SyncTrayIcon(QSystemTrayIcon):
    """BlackboardSync system tray icon."""

    _tooltip = "Blackboard Sync"
    _sync_signal = pyqtSignal()
    _login_signal = pyqtSignal()
    _settings_signal = pyqtSignal()
    _reset_setup_signal = pyqtSignal()
    _quit_signal = pyqtSignal()
    _open_dir_signal = pyqtSignal()
    _show_menu_signal = pyqtSignal()

    def __init__(self):
        """Create a `QSystemTrayIcon`."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        # Create the icon
        icon = Assets.icon()

        # Create the tray
        self.setIcon(icon)
        self.setVisible(True)

        # Create the menu
        self._menu = SyncTrayMenu()

        self._sync_signal = self._menu.refresh.triggered
        self._login_signal = self._menu.log_in.triggered
        self._settings_signal = self._menu.preferences.triggered
        self._reset_setup_signal = self._menu.reset_setup.triggered
        self._quit_signal = self._menu.quit.triggered
        self._open_dir_signal = self._menu.open_dir.triggered
        self._show_menu_signal = self._menu.aboutToShow

        # Add the menu to the tray
        self.setContextMenu(self._menu)
        self.setToolTip(self._tooltip)

    def set_logged_in(self, logged: bool) -> None:
        """Set logged-in status in menu."""
        self._menu.set_logged_in(logged)

    def update_last_synced(self, last: str) -> None:
        """Update last sync time in menu."""
        self._menu.update_last_synced(last)

    def toggle_currently_syncing(self, syncing: bool) -> None:
        """Toggle currently syncing indicator in menu."""
        self._menu.toggle_currently_syncing(syncing)

    def show_msg(self, title: str, msg: str, severity: int = 1, duration: int = 10) -> None:
        """Show the user a message through the tray icon."""
        icons = { 0: QSystemTrayIcon.NoIcon,
                  1: QSystemTrayIcon.Information,
                  2: QSystemTrayIcon.Warning,
                  3: QSystemTrayIcon.Critical }
        duration = duration * 1000
        severity = 0 if severity < 0 or severity > 3 else severity
        self.showMessage(title, msg, icons[severity], duration)

    @property
    def sync_signal(self):
        """Fire if user forces sync."""
        return self._sync_signal

    @property
    def login_signal(self):
        """Fire once user is authenticated."""
        return self._login_signal

    @property
    def settings_signal(self):
        """Fire when the settings menu is opened."""
        return self._settings_signal

    @property
    def reset_setup_signal(self):
        """Fire when the user wants to reset the initial setup."""
        return self._reset_setup_signal

    @property
    def quit_signal(self):
        """Fire once user decides to quit app."""
        return self._quit_signal

    @property
    def open_dir_signal(self):
        """Fire once user wants to open download directory."""
        return self._open_dir_signal

    @property
    def show_menu_signal(self):
        """Fire when menu is about to be shown."""
        return self._show_menu_signal


class RedownloadDialog(QMessageBox):
    """`QMessageBox` shown after a change in download location.

    It consults the user about whether files should be redownloaded to
    the new location or not.
    """

    _window_title = "Redownload all files?"
    _dialog_text = "Should BlackboardSync redownload all files to the new location?"
    _info_text = "Answer no if you intend to move all past downloads manually (Recommended)"

    def __init__(self):
        """Create a `RedownloadDialog`."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self.setText(self._dialog_text)
        self.setInformativeText(self._info_text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.setWindowTitle(self._window_title)
        self.setIcon(QMessageBox.Question)
        self.setWindowIcon(Assets.icon())

    @property
    def redownload(self) -> bool:
        """Indicate if files have to be redownloaded."""
        return self.exec() == QMessageBox.Yes


class UpdateFoundDialog(QMessageBox):
    """`QMessageBox` shown after a more recent version was found."""

    _window_title = "New BlackboardSync release available"
    _dialog_text = "A new version of BlackboardSync is now available!"
    _info_text = "Please download the latest version from the official GitHub repository"

    def __init__(self):
        """Create a `UpdateFoundDialog`."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self.setText(self._dialog_text)
        self.setInformativeText(self._info_text)
        self.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Open)
        self.setWindowTitle(self._window_title)
        self.setIcon(QMessageBox.Information)
        self.setWindowIcon(Assets.icon())

    @property
    def should_update(self) -> bool:
        """Indicate if BBSync should be updated."""
        return self.exec() == QMessageBox.Open


class PersistenceWarning(QDialog):
    """QDialog shown if user chooses to store their login details on their device."""

    _window_title = "Do you wish to stay logged in?"

    def __init__(self):
        """Create instance of PersistenceWarning Dialog."""
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        Assets.load_ui(self)
        self.setWindowTitle(self._window_title)


class SettingsWindow(QWidget):
    """Settings windown UI element."""

    _window_title = "Settings"
    _initial_position = (300, 300)
    _log_out_signal = pyqtSignal()
    _setup_wiz_signal = pyqtSignal()
    _save_signal = pyqtSignal()

    def __init__(self):
        """Create instance of SettingsWindow."""
        super().__init__()
        self.frequency_combo: QComboBox
        self.current_session_label: QLabel
        self.download_location_hint: QLabel
        self._init_ui()

    def _init_ui(self):
        Assets.load_ui(self)

        self.move(*self._initial_position)
        self.setWindowTitle(self._window_title)

        self.select_download_location.clicked.connect(self._choose_location)
        self._log_out_signal = self.log_out_button.clicked
        self._setup_wiz_signal = self.setup_button.clicked
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
        """`Path` of download location."""
        return self._download_location

    @download_location.setter
    def download_location(self, location: Path) -> None:
        self._download_location = location.resolve()
        self.download_location_hint.setText(str(self._download_location))

    @property
    def sync_frequency(self) -> int:
        """Seconds to wait between each sync job."""
        return int([*SyncPeriod][self.frequency_combo.currentIndex()])

    @sync_frequency.setter
    def sync_frequency(self, f: int) -> None:
        self.frequency_combo.setCurrentIndex([*SyncPeriod].index(SyncPeriod(f)))

    @property
    def username(self) -> str:
        """Username of current session."""
        return self.current_session_label.text()

    @username.setter
    def username(self, username: str) -> None:
        if username:
            self.current_session_label.setText(f"Logged in as {username}")
        else:
            self.current_session_label.setText("Not currently logged in")

    @property
    def log_out_signal(self):
        """Fire when user chooses to log out."""
        return self._log_out_signal

    @property
    def setup_wiz_signal(self):
        """Fire when user wants to redo initial setup."""
        return self._setup_wiz_signal

    @property
    def save_signal(self):
        """Fire when settings are saved."""
        return self._save_signal


class LoginWindow(QWidget):
    """Deprecated widget previously used to login."""


class LoginWebView(QWidget):
    """Blackboard login widget."""

    _login_complete_signal = pyqtSignal()

    def __init__(self, start_url: str, target_url: str):
        """Create instance of LoginWebView."""
        super().__init__()
        self.start_url = start_url
        self.target_url = target_url

        self.web_view : QWebEngineView
        self._init_ui()
        self._cookie_jar = RequestsCookieJar()

    def _init_ui(self) -> None:
        Assets.load_ui(self)
        self.web_view.load(QUrl.fromUserInput(self.start_url))
        self.web_view.loadFinished.connect(self._page_load_handler)
        self._cookie_store.cookieAdded.connect(self._cookie_added_handler)

    def _page_load_handler(self) -> None:
        if self.url.startswith(self.target_url):
            self._login_complete_signal.emit()

    def _cookie_added_handler(self, cookie: QNetworkCookie) -> None:
        self._cookie_jar.set(
            cookie.name().data().decode(),
            cookie.value().data().decode(),
            domain=cookie.domain(),
            path=cookie.path(),
            secure=cookie.isSecure()
        )

    def restore(self) -> None:
        self.web_view.setPage(None)
        self.clear_cookie_store()
        self.web_view.load(QUrl.fromUserInput(self.start_url))

    def clear_cookie_store(self) -> None:
        """Clear the HTTP cache and cookies."""
        self._cookie_store.deleteAllCookies()
        self._engine_profile.clearHttpCache()

    @property
    def url(self) -> str:
        """URL of current website."""
        return self.web_view.url().toString()

    @property
    def cookie_jar(self) -> RequestsCookieJar:
        """Contains session cookies of the current session."""
        return self._cookie_jar

    @property
    def _engine_page(self) -> QWebEnginePage:
        return self.web_view.page()

    @property
    def _engine_profile(self) -> QWebEngineProfile:
        return self._engine_page.profile()

    @property
    def _cookie_store(self) -> QWebEngineCookieStore:
        return self._engine_profile.cookieStore()

    @property
    def login_complete_signal(self):
        """Fire when the login flow has completed."""
        return self._login_complete_signal


class SetupWizard(QWizard):
    """Initial setup wizard."""

    class Pages(IntEnum):
        """Pages contained in the wizard."""

        INTRO = 0
        INSTITUTION = 1
        DOWNLOAD_LOCATION = 2
        DOWNLOAD_SINCE = 3
        LAST = 3

    _help_website = 'https://github.com/jacobszpz/BlackboardSync'

    def __init__(self, institutions: list[str]):
        """Create a `SetupWizard`.

        :param list[str] institutions: List of institution names
        """
        super().__init__()

        self.uni_selection_box: QComboBox
        self.since_all_checkbox: QCheckBox
        self.date_spinbox: QSpinBox
        self.institutions = institutions
        self._init_ui()
        self._has_chosen_location = False

    def _init_ui(self):
        Assets.load_ui(self)
        self.uni_selection_box.addItems(self.institutions)
        self.uni_selection_box.clearEditText()

        self.completer = QCompleter(self.institutions, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.uni_selection_box.setCompleter(self.completer)

        self.file_chooser = QFileDialog()
        self.file_chooser.setFileMode(QFileDialog.Directory)
        self.sync_location_button.clicked.connect(self._choose_location)
        self.date_spinbox.setEnabled(False)

        self.since_all_checkbox.stateChanged.connect(
            lambda state: self.date_spinbox.setEnabled(state != Qt.Checked)
        )

        self.uni_selection_page.registerField(
            "userInstitution*",
            self.uni_selection_box.lineEdit()
        )

        self.sync_location_page.registerField(
            "syncLocation*",
            self.sync_location_button,
            property="text",
            changedSignal=self.sync_location_button.clicked
        )

        self.intro_page.setPixmap(QWizard.WatermarkPixmap,
                                  Assets.watermark())

    def initializePage(self, id) -> None:
        if id == self.Pages.DOWNLOAD_LOCATION:
            if self._has_chosen_location:
                self._set_location()

    def validateCurrentPage(self) -> bool:
        """Override QWizard method to validate pages."""
        id = self.currentId()
        valid = True

        if id == self.Pages.INSTITUTION:
            # Do not move forward if institution is not recognised
            if not self._institution_is_valid():
                self._show_not_supported_dialog()
                valid = False

        return valid

    def _set_location(self):
        dir = self.download_location.name or str(self.download_location)
        self.sync_location_button.setText(dir)

    def _choose_location(self):
        if self.file_chooser.exec():
            self._set_location()
            self._has_chosen_location = True

    def _show_not_supported_dialog(self):
        error_dialog = UniNotSupportedDialog(self._help_website)
        error_dialog.exec()

    def _institution_is_valid(self) -> bool:
        return self.field("userInstitution") == self.institution

    @property
    def institution(self) -> str:
        """Text of item selected in institution combo box."""
        return self.uni_selection_box.itemText(self.institution_index)

    @property
    def institution_index(self) -> int:
        """Index of item selected in institution combo box."""
        return self.uni_selection_box.currentIndex()

    @property
    def download_location(self) -> Path:
        """Sync location path selected by user."""
        return Path(self.file_chooser.directory().path())

    @property
    def min_year(self) -> Optional[int]:
        """Courses from this year onward will be downloaded."""
        if not self.since_all_checkbox.isChecked():
            return self.date_spinbox.value()
        return None


class UniNotSupportedDialog(QDialog):
    """`QDialog` about unsupported Blackboard partners."""

    def __init__(self, help_url: str):
        """Create instance of dialog.

        :param str help_url: URL to help website
        """
        super().__init__()
        self._init_ui()
        self._help_url = help_url

    def _init_ui(self):
        Assets.load_ui(self)
        self.button_box.helpRequested.connect(self._open_help_website)

    @pyqtSlot()
    def _open_help_website(self):
        webbrowser.open(self._help_url)
