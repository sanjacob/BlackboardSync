"""
BlackboardSync,
automatically sync content from Blackboard
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

import os
import time
import logging
import platform
import threading
import subprocess
from pathlib import Path
from requests.exceptions import ConnectionError
from datetime import datetime, timezone, timedelta

from .blackboard import BlackboardSession
from .download import BlackboardDownload
from .config import SyncConfig


class BlackboardSync:
    """Represents an instance of the BlackboardSync application."""
    _log_directory = "log"
    _app_name = 'blackboard_sync'

    # Filters out non-subjects from blackboard (may need more testing)
    _data_source = "_21_1"

    # Seconds between each check of time elapsed since last sync
    _check_sleep_time = 10
    # Sync thread max retries
    _max_retries = 3

    _logger = logging.getLogger(__name__)

    def __init__(self):
        # Time between each sync in seconds
        self._sync_interval = 60 * 30

        # Default download location
        self._sync_dir = Path(Path.home(), 'Downloads', 'BlackboardSync',)
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
        self._is_active = False

        # Set up logging
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

        # Obtain user configuration dir
        self._config = SyncConfig()

        if self._config_file.exists():
            self.logger.info("Preexisting configuration exists")
            self._load_config()

    def auth(self, username: str, password: str, persistence: bool = False) -> bool:
        """Create a new Blackboard session with the given credentials.
        Will start syncing automatically if login successful.

        :param str username: Institutional email address (e.g. example@uclan.ac.uk).
        :param str password: Password of the account.
        :param bool persistence: If true, login will be saved in the OS designated keyring.
        """
        username = username.strip()
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

    def _load_config(self) -> None:
        """Load saved preferences from disk."""
        self._last_sync = self._config.latest_sync
        self._update_next_sync()
        self._sync_dir = self._config.location
        self.auth(username=self._config.username, password=self._config.password)

    # def _update_last_sync(self, sync_config: SyncConfig) -> SyncConfig:
    #     sync_config['last_sync'] = self.last_sync.isoformat()
    #     return sync_config

    # def _update_sync_dir(self, sync_config: SyncConfig) -> SyncConfig:
    #     sync_config['location'] = str(self.sync_dir)
    #     return sync_config

    def _delete_last_sync(self, sync_config: SyncConfig) -> SyncConfig:
        sync_config.pop('last_sync', None)
        return sync_config

    # def _save_login_config(self, login_config: ConfigDict,
    #                        username: str, password: str) -> ConfigDict:
    #     login_config['username'] = username
    #     keyring.set_password(self._config_filename, username, password)
    #     return login_config

    @_update_config()
    def _delete_login_config(self, config: ConfigDict) -> ConfigDict:
        config.pop('Login', None)
        keyring.delete_password(self._config_filename, self.username)
        return config

    def log_out(self, hard_reset: bool = True) -> None:
        """Stop syncing and forget user session.

        :param bool hard_reset: If true, login details will be removed from
            saved configuration.
        """
        self.stop_sync()
        self.sess = None
        self._is_logged_in = False

        if hard_reset:
            self._delete_login_config()

        self._username = ""

    def _sync_task(self) -> None:
        """Method run by Sync thread. Constantly checks if last sync is outdated
        and starts a new download job if so.
        """
        reload_session = False
        failed_attempts = 0

        while self._is_active:
            if self.outdated or self._force_sync:
                self.logger.debug("Syncing now")
                self._is_syncing = True

                # Download from last datetime
                new_download = BlackboardDownload(self.sess, self.sync_dir / '', self.last_sync)

                try:
                    self.last_sync = new_download.download()
                    failed_attempts = 0
                except ValueError:
                    # Session expired, log out and attempt to reload config
                    self.logger.warning("User session expired")
                    reload_session = True
                    self.log_out(hard_reset=False)
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

        if reload_session:
            self._load_config()

    def start_sync(self) -> None:
        """Stars Sync thread."""
        self.logger.info("Starting sync thread")
        self._is_active = True
        self.sync_thread = threading.Thread(target=self._sync_task)
        self.sync_thread.start()

    def stop_sync(self) -> None:
        """Stops Sync thread."""
        self.logger.info("Stopping sync thread")
        self._is_active = False

    def _log_exception(self, e: Exception) -> None:
        """Log exception to log file inside sync location."""
        self._log_dir.mkdir(exist_ok=True, parents=True)
        exception_log = logging.FileHandler(self._log_path)
        self.logger.addHandler(exception_log)
        self.logger.exception("Exception in sync thread")
        self.logger.removeHandler(exception_log)

    def open_sync_dir(self) -> None:
        """Starts a subprocess to open the default file explorer at the sync location."""
        self.logger.debug("Opening sync dir on file explorer")
        if platform.system() == "Windows":
            os.startfile(self.sync_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.sync_dir])
        else:
            subprocess.Popen(["xdg-open", self.sync_dir])

    def force_sync(self) -> None:
        """Forces Sync thread to start download job ASAP."""
        self.logger.debug("Forced syncing")
        self._force_sync = True

    @property
    def _log_path(self) -> Path:
        filename = f"sync_error_{datetime.now():%Y-%m-%dT%H_%M_%S_%f}.log"
        return Path(self._log_dir / filename)

    @property
    def _log_dir(self) -> Path:
        return Path(self.sync_dir / self._log_directory)

    @property
    def username(self) -> str:
        """Last username used to login."""
        return self._username

    @property
    def last_sync(self) -> datetime:
        """Datetime right before last download job started."""
        return self._last_sync

    @last_sync.setter
    def last_sync(self, last: datetime):
        self._last_sync = last
        self._update_last_sync()
        self._update_next_sync()

    def _update_next_sync(self) -> None:
        """Stores a calculated datetime when next sync should take place."""
        self._next_sync = (self.last_sync + timedelta(seconds=self._sync_interval))

    @property
    def next_sync(self) -> datetime:
        """Calculated time when last sync will be outdated."""
        return self._next_sync

    @property
    def outdated(self) -> bool:
        """Returns true if last download job is outdated."""
        if self.last_sync is None:
            return True
        return datetime.now(timezone.utc) >= self.next_sync

    @property
    def data_source(self) -> str:
        """Filters the modules to download."""
        # The default works in my testing. However, this might need tweaking for other users,
        # specially if used for different institutions than UCLan.
        return self._data_source

    @data_source.setter
    def data_source(self, d: str) -> None:
        self._data_source = d

    @property
    def sync_dir(self) -> Path:
        """The location to where all Blackboard content will be downloaded."""
        return self._sync_dir

    def set_sync_dir(self, dir: Path, redownload: bool = False) -> None:
        """Sets new sync location.

        :param Path dir: The path of the sync dir.
        :param bool redownload: If true, ALL content will be re-downloaded to the new location.
        """
        if dir != self.sync_dir:
            self._sync_dir = dir
            self._update_sync_dir()

            if redownload:
                # Unset last sync time to fully download all files in new location
                self._last_sync = None
                self._delete_last_sync()

    @property
    def sync_interval(self) -> int:
        """The time to wait between download jobs."""
        return self._sync_interval

    @sync_interval.setter
    def sync_interval(self, p: int) -> None:
        self._sync_interval = p

    @property
    def is_active(self) -> bool:
        """Indicates the state of the sync thread."""
        return self._is_active

    @property
    def is_logged_in(self) -> bool:
        """Indicates if a user session is currently active."""
        return self._is_logged_in

    @property
    def is_syncing(self) -> bool:
        """Flag raised everytime a download job is running."""
        return self._is_syncing

    @property
    def logger(self) -> logging.Logger:
        """Logger for BlackboardSync, set at level WARN."""
        return self._logger
