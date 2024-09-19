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

import sys
from pathlib import Path
from datetime import datetime
from requests.cookies import RequestsCookieJar
from importlib.metadata import version, PackageNotFoundError

from PyQt6.QtCore import QLocale, QTranslator, QLibraryInfo
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QWidget

from . import SetupWizard, LoginWebView, SettingsWindow, SyncTrayIcon
from .notification import Event
from .dialogs import Dialogs
from .utils import add_to_startup, open_in_file_browser
from .assets import get_translations


class UIManager(QObject):
    class Signals(QObject):
        open_settings = pyqtSignal()
        open_tray = pyqtSignal(bool)
        open_menu = pyqtSignal()
        open_downloads = pyqtSignal()
        setup = pyqtSignal(int, Path, int)
        config = pyqtSignal(Path, int)
        force_sync = pyqtSignal()
        log_out = pyqtSignal()
        log_in = pyqtSignal(RequestsCookieJar)
        redownload = pyqtSignal()
        quit = pyqtSignal()

    def __init__(self, id: str, title: str, uri: str,
                 universities: list[str], autodetected: int | None) -> None:
        super().__init__()
        self.id = id
        self.title = title
        self.uri = uri
        self.help_uri = f"{uri}/issues"

        self.signals = self.Signals()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(title)
        self.app.setQuitOnLastWindowClosed(False)
        self.load_translator()

        try:
            __version__ = version(Path(__file__).parent.parent.stem)
        except PackageNotFoundError:
            pass
        else:
            self.app.setApplicationVersion(__version__)

        self._init_ui(universities, autodetected)

    def _init_ui(self, universities: list[str],
                 autodetected: int | None) -> None:
        self.setup_window = SetupWizard(self.help_uri,
                                        universities, autodetected)
        self.login_window = LoginWebView(self.help_uri)
        self.config_window = SettingsWindow()
        self.tray = SyncTrayIcon()
        self.dialogs = Dialogs()

        self.login_window.signals.login_complete.connect(self.slot_log_in)
        self.setup_window.accepted.connect(self.slot_setup)

        self.config_window.signals.log_out.connect(self.signals.log_out)
        self.config_window.signals.save.connect(self.slot_config)
        self.config_window.signals.log_out.connect(self.slot_log_out)
        self.config_window.signals.setup_wiz.connect(self.slot_open_setup)

        self.tray.signals.force_sync.connect(self.signals.force_sync)
        self.tray.signals.show_menu.connect(self.signals.open_menu)
        self.tray.signals.settings.connect(self.signals.open_settings)
        self.tray.signals.open_dir.connect(self.signals.open_downloads)
        self.tray.signals.quit.connect(self.signals.quit)
        self.tray.signals.reset_setup.connect(self.slot_open_setup)
        self.tray.activated.connect(self.slot_open_tray)
        self.tray.signals.quit.connect(self.slot_quit)

    def load_translator(self) -> None:
        tr_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        self.locale = QLocale.system().name()

        translations = [
            ('qtbase_{}', tr_path),
            ('qtwebengine_{}', tr_path),
            ('{}', get_translations())
        ]

        self.translators = []

        for filename, path in translations:
            translator = QTranslator()

            if translator.load(filename.format(self.locale), path):
                self.app.installTranslator(translator)
                self.translators.append(translator)

    def start(self, first_time: bool) -> None:
        if first_time:
            add_to_startup(self.id)
            self.show(self.setup_window)
        else:
            self.show(self.login_window)

        self.app.exec()

    def show(self, widget: QWidget) -> None:
        widget.setWindowState(Qt.WindowState.WindowNoState)
        widget.show()
        widget.setFocus()

    def hide(self, widget: QWidget) -> None:
        widget.setVisible(False)

    @pyqtSlot(QSystemTrayIcon.ActivationReason)
    def slot_open_tray(self,
                       reason: QSystemTrayIcon.ActivationReason) -> None:
        clicked = reason == QSystemTrayIcon.ActivationReason.Trigger
        self.signals.open_tray.emit(clicked)

    @pyqtSlot()
    def slot_log_out(self) -> None:
        self.tray.set_logged_in(False)
        self.login_window.restore()
        self.show(self.login_window)
        self.hide(self.config_window)

    @pyqtSlot()
    def slot_open_setup(self) -> None:
        self.signals.log_out.emit()
        self.hide(self.login_window)
        self.hide(self.config_window)
        self.show(self.setup_window)

    @pyqtSlot()
    def slot_log_in(self) -> None:
        self.signals.log_in.emit(self.login_window.cookies)

    def log_in(self) -> None:
        self.hide(self.login_window)
        self.tray.set_logged_in(True)

    @pyqtSlot()
    def slot_setup(self) -> None:
        self.hide(self.setup_window)

        self.signals.setup.emit(self.setup_window.institution_index,
                                self.setup_window.download_location,
                                self.setup_window.min_year or 0)

    @pyqtSlot()
    def slot_config(self) -> None:
        self.hide(self.config_window)
        self.signals.config.emit(self.config_window.download_location,
                                 self.config_window.sync_frequency)

    @pyqtSlot()
    def slot_quit(self) -> None:
        self.login_window.cancel_watchdog()
        self.app.quit()

    def open_settings(self, download_location: Path, username: str,
                      sync_interval: int, version: str | None) -> None:
        self.config_window.download_location = download_location
        self.config_window.username = username
        self.config_window.sync_frequency = sync_interval
        self.config_window.version = version
        self.show(self.config_window)

    def open_menu(self, last_sync: datetime,
                  is_logged: bool, is_syncing: bool) -> None:
        self.tray.set_last_synced(last_sync)
        self.tray.set_logged_in(is_logged)
        self.tray.set_currently_syncing(is_syncing)

    def open_tray(self, first_time: bool, is_logged: bool) -> None:
        if first_time:
            self.show(self.setup_window)
        elif not is_logged:
            self.show(self.login_window)

    def open_file(self, file: Path) -> None:
        open_in_file_browser(file)

    def open_login(self, start_url: str, target_url: str) -> None:
        self.login_window.load(start_url, target_url)
        self.show(self.login_window)

    def ask_redownload(self) -> None:
        if self.dialogs.redownload_dialog():
            self.signals.redownload.emit()

    def notify_running(self) -> None:
        self.tray.notify(Event.APP_RUNNING)

    def notify_login_error(self) -> None:
        self.dialogs.login_error_dialog(self.help_uri)
        self.login_window.restore()
        self.show(self.login_window)

    def notify_sync_error(self) -> None:
        self.tray.notify(Event.DOWNLOAD_ERROR)

    def notify_update(self) -> None:
        self.tray.notify(Event.UPDATE_AVAILABLE)
