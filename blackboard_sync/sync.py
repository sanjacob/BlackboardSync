"""
BlackboardSync.

Automatically sync content from Blackboard
"""

# Copyright (C) 2023, Jacob Sánchez Pérez

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

import time
import logging
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

from requests.cookies import RequestsCookieJar

from .config import SyncConfig
from .download import BlackboardDownload

from blackboard.api_extended import BlackboardExtended
from blackboard.exceptions import BBUnauthorizedError, BBForbiddenError

from .institutions import Institution, get_by_index

logger = logging.getLogger(__name__)


class BlackboardSync:
    """Represents an instance of the BlackboardSync application."""

    _log_directory = "log"
    _app_name = 'blackboard_sync'

    # Seconds between each check of time elapsed since last sync
    _check_sleep_time = 10
    # Sync thread max retries
    _max_retries = 3


    def __init__(self):
        """Create an instance of the program."""

        # Download job
        self._download = None

        # Time between each sync in seconds
        self._sync_interval = 60 * 30

        # Time of next programmed sync
        self._next_sync = None
        # User session active
        self._is_logged_in = False

        # Flag to force sync
        self._force_sync = False
        # Flag to know if syncing is in progress
        self._is_syncing = False
        # Flag to know if syncing is on
        self._is_active = False
        # Flag to know if download thread has errors
        self._has_error = False

        logger.debug("Initialising BlackboardSync")

        self.university : Optional[Institution] = None
        self.sess : Optional[BlackboardSession] = None

        # Attempt to load existing configuration
        self._config = SyncConfig()
        logger.info("Loading preexisting configuration")

        if self._config.university_index is not None:
            self.university = get_by_index(self._config.university_index)

        if self._config.last_sync_time is not None:
            self._update_next_sync()

        if self.download_location is not None:
            self._add_logger_file_handler()

    def setup(self, university_index: int, download_location: Path,
              min_year: Optional[int] = None) -> None:
        """Setup the university information."""
        self.university_index = university_index
        self.download_location = download_location

        # If min_year has decreased, redownload
        if (self._config.min_year or 0) > (min_year or 0):
            self.redownload()

        self._config.min_year = min_year

    def auth(self, cookie_jar: RequestsCookieJar) -> bool:
        """Create a new Blackboard session with the given cookies."""
        if self.university is None:
            return False

        self._cookies = cookie_jar
        api_url = str(self.university.api_url)

        try:
            u_sess = BlackboardExtended(api_url, cookies=cookie_jar)
        except (BBUnauthorizedError, BBForbiddenError):
            logger.warning("Credentials are incorrect")
        else:
            logger.info("Logged in successfully")
            self.sess = u_sess
            self._is_logged_in = True
            self.start_sync()

        return self._is_logged_in

    def log_out(self) -> None:
        """Stop syncing and forget user session."""
        self.stop_sync()
        self.sess = None
        self._is_logged_in = False

    def _sync_task(self) -> None:
        """Constantly check if the data is outdated and if so start a download job.

        Method run by Sync thread.
        """
        reload_session = False
        failed_attempts = 0

        while self._is_active:
            if self.outdated or self._force_sync:
                logger.debug("Syncing now")
                self._is_syncing = True

                # Download from last datetime
                user_session = self.sess

                if user_session is not None and self.university is not None:
                    self._download = BlackboardDownload(user_session,
                                                        self.download_location,
                                                        self.last_sync_time,
                                                        self.min_year)

                try:
                    if not self._is_active:
                        self._download.cancel()
                    job_start_time = self._download.download()
                    if job_start_time is not None:
                        self.last_sync_time = job_start_time
                    failed_attempts = 0
                except BBUnauthorizedError:
                    logger.exception("User session expired")
                    reload_session = True
                    self.log_out()

                # Could not sync
                if failed_attempts >= self._max_retries:
                    self.log_out()

                # Reset force sync flag
                self._force_sync = False
                self._is_syncing = False
            if self._is_active:
                time.sleep(self._check_sleep_time)

        if reload_session:
            self.auth(self._cookies)

    def start_sync(self) -> bool:
        """Starts Sync thread or returns False if not possible."""
        if self._has_error:
            return False
        logger.info("Starting sync thread")
        self._is_active = True
        self.sync_thread = threading.Thread(target=self._sync_task)
        self.sync_thread.start()
        return True

    def stop_sync(self) -> None:
        """Stop Sync thread."""
        logger.info("Stopping sync thread")
        self._is_active = False

        if self._download is not None:
            self._download.cancel()

    def _add_logger_file_handler(self) -> None:
        filename = f"sync_log_{datetime.now():%Y-%m-%d}.log"

        #log_dir = Path(self.download_location / self._log_directory)
        #log_dir.mkdir(exist_ok=True, parents=True)

        #log_path = Path(log_dir / filename)

        #logger = logging.getLogger(__name__)

        #file_handler = logging.FileHandler(log_path)
        #file_handler.setLevel(logging.ERROR)

        #logger.addHandler(file_handler)

    def force_sync(self) -> None:
        """Force Sync thread to start download job ASAP."""
        logger.debug("Forced syncing")
        self._force_sync = True

    def redownload(self) -> None:
        self.last_sync_time = None

    @property
    def username(self) -> Optional[str]:
        return self.sess.user_id if self.sess is not None else None

    @property
    def last_sync_time(self) -> Optional[datetime]:
        """Datetime right before last download job started."""
        return self._config.last_sync_time

    @last_sync_time.setter
    def last_sync_time(self, last_time: Optional[datetime]):
        """Updates the last sync time recorded."""
        self._config.last_sync_time = last_time
        self._update_next_sync()

    def _update_next_sync(self) -> None:
        """Store a calculated datetime when next sync should take place."""
        if self.last_sync_time is not None:
            self._next_sync = (self._config.last_sync_time +
                               timedelta(seconds=self._sync_interval))

    @property
    def next_sync(self) -> datetime:
        """Time when last sync will be outdated."""
        return self._next_sync

    @property
    def outdated(self) -> bool:
        """Return true if last download job is outdated."""
        if self._config.last_sync_time is None:
            return True
        return datetime.now(timezone.utc) >= self.next_sync

    @property
    def min_year(self) -> int:
        return self._config.min_year

    @property
    def university_index(self):
        return self._config.university_index

    @university_index.setter
    def university_index(self, uni_index: int) -> None:
        self._config.university_index = uni_index
        self.university = get_by_index(uni_index)

    @property
    def download_location(self) -> Path:
        """Location to where all Blackboard content will be downloaded."""
        return self._config.download_location

    @download_location.setter
    def download_location(self, value) -> None:
        if value != self.download_location:
            self._config.download_location = value
            self._add_logger_file_handler()

    @property
    def sync_interval(self) -> int:
        """Time to wait between download jobs."""
        return self._sync_interval

    @sync_interval.setter
    def sync_interval(self, p: int) -> None:
        self._sync_interval = p

    @property
    def is_active(self) -> bool:
        """Indicate the state of the sync thread."""
        return self._is_active

    @property
    def is_logged_in(self) -> bool:
        """Indicate if a user session is currently active."""
        return self._is_logged_in

    @property
    def is_syncing(self) -> bool:
        """Flag raised everytime a download job is running."""
        return self._is_syncing

    @property
    def has_error(self) -> bool:
        """Flag indicates an error resulting in no downloads."""
        return self._has_error
