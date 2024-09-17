"""
Blackboard Sync

Download your Blackboard Learn content automatically.
"""

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

import time
import logging
import threading
from pathlib import Path
from requests import RequestException
from datetime import datetime, timezone, timedelta

from requests.cookies import RequestsCookieJar

from blackboard.api_extended import BlackboardExtended
from blackboard.exceptions import BBUnauthorizedError, BBForbiddenError

from .config import SyncConfig
from .download import BlackboardDownload
from .institutions import Institution, get_by_index

logger = logging.getLogger(__name__)


class BlackboardSync:
    """Represents an instance of the BlackboardSync application."""

    _log_directory = "log"

    # Seconds between each check of time elapsed since last sync
    _check_sleep_time = 10

    def __init__(self) -> None:
        """Create an instance of the program."""

        # Download job
        self._download: BlackboardDownload | None = None

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

        self.university: Institution | None = None
        self.sess: BlackboardExtended | None = None

        # Attempt to load existing configuration
        self._config = SyncConfig()
        logger.info("Loading preexisting configuration")

        if self._config.university_index is not None:
            self.university = get_by_index(self._config.university_index)

        if self._config.last_sync_time is not None:
            self.schedule_next_sync(self._config.last_sync_time)

        if self.download_location is not None:
            self._add_logger_file_handler()

    def setup(self, university_index: int, download_location: Path,
              min_year: int | None = None) -> None:
        """Setup the university information."""
        self.university_index = university_index
        self.download_location = download_location

        # If min_year has decreased, redownload
        if (self._config.min_year or 0) > (min_year or 0):
            self.redownload()

        self._config.min_year = min_year

    def auth(self, cookies: RequestsCookieJar) -> bool:
        """Create a new Blackboard session with the given cookies."""
        if self.university is None:
            return False

        api_url = str(self.university.api_url)

        try:
            u_sess = BlackboardExtended(api_url, cookies=cookies)
            # should trigger exception if not authenticated
            u_sess.fetch_users(user_id='me')
        except (BBUnauthorizedError, BBForbiddenError):
            logger.warning("Credentials are incorrect")
        except RequestException:
            logger.warning("Error while making auth request")
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

    def download(self) -> datetime | None:
        user_session = self.sess

        if user_session is None or self.university is None:
            return None

        if self.download_location is None:
            return None

        self._download = BlackboardDownload(
            user_session,
            self.download_location,
            self.last_sync_time,
            self.min_year
        )

        if not self._is_active:
            return None

        try:
            start_time = self._download.download()
        except BBUnauthorizedError:
            logger.exception("User session expired")
            self.log_out()
        except RequestException:
            logger.exception("Network failure")
            self._has_error = True

            # manually postpone next sync job
            self.schedule_next_sync(datetime.now(timezone.utc))
        else:
            return start_time
        return None

    def _sync_task(self) -> None:
        """Constantly check if data is outdated and if so start download.

        Method run by Sync thread.
        """
        while self._is_active:
            if self.outdated or self._force_sync:
                logger.info("Syncing now")
                self._is_syncing = True

                start_time = self.download()

                if start_time is not None:
                    self.last_sync_time = start_time

                # Reset sync flags
                self._force_sync = False
                self._is_syncing = False

            if self._is_active:
                time.sleep(self._check_sleep_time)

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

        if self.download_location is None:
            return

        log_dir = Path(self.download_location / self._log_directory)
        log_dir.mkdir(exist_ok=True, parents=True)

        log_path = Path(log_dir / filename)

        logger = logging.getLogger(__name__)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.ERROR)

        logger.addHandler(file_handler)

    def force_sync(self) -> None:
        """Force Sync thread to start download job ASAP."""
        logger.debug("Forced syncing")
        self._force_sync = True

    def redownload(self) -> None:
        self.last_sync_time = None

    @property
    def username(self) -> str | None:
        return self.sess.user_id if self.sess is not None else None

    @property
    def last_sync_time(self) -> datetime | None:
        """Datetime right before last download job started."""
        return self._config.last_sync_time

    @last_sync_time.setter
    def last_sync_time(self, last_time: datetime | None) -> None:
        """Updates the last sync time recorded."""
        self._config.last_sync_time = last_time
        self.schedule_next_sync(last_time)

    def schedule_next_sync(self, start_time: datetime | None) -> None:
        if start_time is not None:
            delay = timedelta(seconds=self._sync_interval)
            self._next_sync = start_time + delay

    @property
    def next_sync(self) -> datetime | None:
        """Time when last sync will be outdated."""
        return self._next_sync

    @property
    def outdated(self) -> bool:
        """Return true if last download job is outdated."""
        if self.next_sync is None:
            return True
        return datetime.now(timezone.utc) >= self.next_sync

    @property
    def min_year(self) -> int | None:
        return self._config.min_year

    @property
    def university_index(self) -> int | None:
        return self._config.university_index

    @university_index.setter
    def university_index(self, uni_index: int) -> None:
        self._config.university_index = uni_index
        self.university = get_by_index(uni_index)

    @property
    def download_location(self) -> Path | None:
        """Location to where all the content will be downloaded."""
        return self._config.download_location

    @download_location.setter
    def download_location(self, value: Path) -> None:
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
        if self._has_error:
            self._has_error = False
            return True
        return False
