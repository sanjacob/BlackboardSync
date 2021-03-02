#!/usr/bin/env python3

"""
BlackboardSync,
automatically sync content from Blackboard

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

import os
import time
import toml
import logging
import threading
import platform
import subprocess
from pathlib import Path
from appdirs import user_config_dir
from requests.exceptions import ConnectionError
from datetime import datetime, timezone, timedelta
from blackboard.api import BlackboardSession
from download import BlackboardDownload

from __about__ import __author__


class BlackboardSync:
    _config_filename = "blackboard_sync"
    _log_directory = "Logs"

    # Filters out non-subjects from blackboard (may need more testing)
    _data_source = "_21_1"

    # Seconds between each check of time elapsed since last sync
    _check_sleep_time = 10
    # Sync thread max retries
    _max_retries = 3

    logger = logging.getLogger(__name__)

    def __init__(self):
        # Time between each sync in seconds
        self._sync_period = 60 * 30

        # Default download location
        self._sync_folder = Path(Path.home(), 'Downloads', 'BlackboardSync')
        # Time before last sync
        self._last_sync = None
        # Time of next programmed sync
        self._next_sync = None
        # User session active
        self._is_logged_in = False
        self._username = ""

        # Flag to force sync
        self._force_sync = False
        # Flag to know if syncing is in progress
        self._is_syncing = False
        # Flag to know if syncing is on
        self._sync_on = False

        self.logger.setLevel(logging.WARN)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.debug("Initialising BlackboardSync")

        sess_logger = logging.getLogger("BlackboardSession")
        sess_logger.setLevel(logging.WARN)
        sess_logger.addHandler(logging.StreamHandler())

        download_logger = logging.getLogger("BlackboardDownload")
        download_logger.setLevel(logging.WARN)
        download_logger.addHandler(logging.StreamHandler())

        self.sess_logger = sess_logger
        self.download_logger = download_logger

        config_folder = Path(user_config_dir(appauthor=__author__, roaming=True))
        self._config_file = (config_folder / self._config_filename)

        if self._config_file.exists():
            self.logger.info("Preexisting configuration exists")
            self.load_config()

    def auth(self, username, password, persistence=False) -> bool:
        try:
            u_sess = BlackboardSession(username, password)
        except ValueError:
            self.logger.warning("Credentials are incorrect")
        else:
            self.logger.info("Logged in successfully")
            self.sess = u_sess
            self._username = u_sess.username
            self._is_logged_in = True

            if persistence:
                self._save_login_config(username, password)

            self.start_sync()
        return self._is_logged_in

    def load_config(self) -> bool:
        with self._config_file.open() as config_file:
            config = toml.load(config_file)

            if config:
                if 'Sync' in config:
                    if 'last_sync' in (sync_conf := config['Sync']):
                        self._last_sync = datetime.fromisoformat(sync_conf['last_sync'])
                        self._update_next_sync()
                    if 'location' in sync_conf:
                        self._sync_folder = Path(sync_conf['location'])
                if 'Login' in config:
                    self.auth(**config['Login'])

    def _update_config(func):
        def update_config_wrapper(self, *args, **kwargs):
            """Acts as wrapper for any method that modifies the existing configuration
            """
            if not self._config_file.exists():
                self._config_file.touch()

            with self._config_file.open("r+") as config_file:
                config = toml.load(config_file)
                modified_config = func(self, config, *args, **kwargs)

                config_file.seek(0)
                config_file.truncate()
                toml.dump(modified_config, config_file)
                self.logger.info("Updated configuration file")
        return update_config_wrapper

    @_update_config
    def _update_last_sync(self, config):
        if 'Sync' not in config:
            config['Sync'] = {}

        config['Sync']['last_sync'] = self.last_sync.isoformat()
        return config

    @_update_config
    def _update_sync_folder(self, config):
        if 'Sync' not in config:
            config['Sync'] = {}

        config['Sync']['location'] = str(self.sync_folder)
        return config

    @_update_config
    def _save_login_config(self, config, username, password):
        config['Login'] = {'username': username,
                           'password': password}
        return config

    @_update_config
    def _delete_login_config(self, config):
        config.pop('Login', None)
        return config

    @_update_config
    def _delete_last_sync(self, config):
        if 'Sync' in config:
            config['Sync'].pop('last_sync', None)
        return config

    def log_out(self, hard_reset=True):
        self.stop_sync()
        self.sess = None
        self._username = ""
        self._is_logged_in = False

        if hard_reset:
            self._delete_login_config()

    def sync_task(self):
        """Check if current time is greater than last download + x, every n seconds
        """
        reload_session = False
        failed_attempts = 0

        while self._sync_on:
            if self.outdated or self._force_sync:
                self.logger.debug("Syncing now")
                self._is_syncing = True

                # Download from last datetime
                new_download = BlackboardDownload(self.sess, self.sync_folder, self.last_sync)

                try:
                    self.last_sync = new_download.download()
                    failed_attempts = 0
                except ValueError:
                    # Session expired, log out and attempt to reload config
                    self.logger.warning("User session expired")
                except ConnectionError as e:
                    # Random python connection error
                    self._log_exception(e)
                    failed_attempts += 1

                # Could not sync
                if failed_attempts >= self._max_retries:
                    self.log_out(hard_reset=False)

                # Reset force sync flag
                self._force_sync = False
                self._is_syncing = False
            time.sleep(self._check_sleep_time)

    def start_sync(self):
        self.logger.info("Starting sync thread")
        self._sync_on = True
        self.sync_thread = threading.Thread(target=self.sync_task)
        self.sync_thread.start()

    def stop_sync(self):
        self._sync_on = False

    def _log_exception(self, e):
        # Log exception to log file
        self._log_folder.mkdir(exist_ok=True, parents=True)
        exception_log = logging.FileHandler(self._log_path)
        self.logger.addHandler(exception_log)
        self.logger.exception("Exception in sync thread")
        self.logger.removeHandler(exception_log)

    def open_sync_folder(self):
        self.logger.debug("Opening sync folder on file explorer")
        if platform.system() == "Windows":
            os.startfile(self.sync_folder)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.sync_folder])
        else:
            subprocess.Popen(["xdg-open", self.sync_folder])

    def force_sync(self):
        self.logger.debug("Forced syncing")
        self._force_sync = True

    @property
    def _log_path(self) -> Path:
        filename = f"sync_error_{datetime.now():%Y-%m-%dT%H_%M_%S_%f}.log"
        return Path(self._log_folder / filename)

    @property
    def _log_folder(self) -> Path:
        return Path(self.sync_folder / self._log_directory)

    @property
    def username(self) -> str:
        return self._username

    @property
    def last_sync(self) -> datetime:
        return self._last_sync

    @last_sync.setter
    def last_sync(self, last: datetime):
        self._last_sync = last
        self._update_last_sync()
        self._update_next_sync()

    def _update_next_sync(self):
        self._next_sync = (self.last_sync + timedelta(seconds=self._sync_period))

    @property
    def next_sync(self) -> datetime:
        return self._next_sync

    @property
    def outdated(self) -> bool:
        if self.last_sync is None:
            return True
        return datetime.now(timezone.utc) >= self.next_sync

    @property
    def data_source(self) -> str:
        return self._data_source

    @data_source.setter
    def data_source(self, d: str):
        self._data_source = d

    @property
    def sync_folder(self) -> Path:
        return self._sync_folder

    def set_sync_folder(self, folder: Path, redownload: bool = False):
        if folder != self.sync_folder:
            self._sync_folder = folder
            self._update_sync_folder()

            if redownload:
                # Unset last sync time to fully download all files in new location
                self._last_sync = None
                self._delete_last_sync()

    @property
    def sync_period(self) -> int:
        return self._sync_period

    @sync_period.setter
    def sync_period(self, p: int):
        self._sync_period = p

    @property
    def sync_on(self) -> bool:
        return self._sync_on

    @property
    def is_logged_in(self) -> bool:
        return self._is_logged_in

    @property
    def is_syncing(self) -> bool:
        return self._is_syncing


if __name__ == '__main__':
    pass
