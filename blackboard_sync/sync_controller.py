#!/usr/bin/env python3

"""BlackboardSync Controller."""

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

from requests.cookies import RequestsCookieJar
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version

from .sync import BlackboardSync
from .__about__ import __id__, __title__, __uri__
from .institutions import get_names, autodetect

from .updates import check_for_updates
from .qt.manager import UIManager


class SyncController:
    """Connects an instance of BlackboardSync with the UI module."""

    def __init__(self):
        super().__init__()
        self.model = BlackboardSync()
        self.ui = UIManager(__id__, __title__, __uri__,
                            get_names(), autodetect())

        first_time = self.model.university is None

        if not first_time:
            self.open_login()

        self.init_signals()
        self.ui.start(first_time)

    def init_signals(self):
        self.ui.signals.open_settings.connect(self.open_settings)
        self.ui.signals.open_tray.connect(self.open_tray)
        self.ui.signals.open_downloads.connect(self.open_downloads)
        self.ui.signals.open_menu.connect(self.open_menu)
        self.ui.signals.setup.connect(self.setup)
        self.ui.signals.config.connect(self.config)
        self.ui.signals.redownload.connect(self.redownload)
        self.ui.signals.force_sync.connect(self.force_sync)
        self.ui.signals.log_in.connect(self.log_in)
        self.ui.signals.log_out.connect(self.log_out)
        self.ui.signals.quit.connect(self.quit)

    def open_login(self) -> None:
        start_url = str(self.model.university.login.start_url)
        target_url = str(self.model.university.login.target_url)

        self.ui.open_login(start_url, target_url)

    def force_sync(self) -> None:
        self.model.force_sync()

    def open_settings(self) -> None:
        __version__ = None
        package = __package__.replace('_', '')

        try:
            __version__ = get_version(package)
        except PackageNotFoundError:
            pass

        self.ui.open_settings(self.model.download_location,
                              self.model.username,
                              self.model.sync_interval,
                              __version__)

    def open_menu(self) -> None:
        self.ui.open_menu(self.model.last_sync_time,
                          self.model.is_logged_in,
                          self.model.is_syncing)

        if self.model.has_error:
            self.ui.notify_sync_error()

    def open_tray(self, clicked) -> None:
        if clicked:
            first_time = self.model.university is None
            is_logged_in = self.model.is_logged_in

            self.ui.open_tray(first_time, is_logged_in)

    def open_downloads(self) -> None:
        self.ui.open_file(self.model.download_location)

    def setup(self, institution_index: int,
              download_location: str, min_year: int) -> None:
        self.model.setup(institution_index, download_location, min_year)
        self.open_login()

    def config(self, download_location: str, sync_frequency: int) -> None:
        if self.model.download_location != download_location:
            self.model.download_location = download_location
            self.ui.ask_redownload()

        self.model.sync_interval = sync_frequency

    def redownload(self) -> None:
        self.model.redownload()

    def log_in(self, cookies: RequestsCookieJar) -> None:
        if self.model.auth(cookies):
            self.ui.log_in()
            self.ui.notify_running()
            self.check_for_updates()
        else:
            self.ui.notify_login_error()

    def log_out(self) -> None:
        if self.model.is_active:
            self.model.stop_sync()

        self.model.log_out()

    def quit(self) -> None:
        if self.model.is_active:
            self.model.stop_sync()

    def check_for_updates(self) -> None:
        if check_for_updates():
            self.ui.notify_update()


if __name__ == '__main__':
    controller = SyncController()
