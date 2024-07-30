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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from datetime import datetime, timezone
import threading

from .content import download, D

_logger = logging.getLogger(__name__)

class SyncThread(threading.Thread):
    def __init__(self):
        self.is_active = False

    def run(self):
        while self.is_active:
            if self.is_outdated or self.is_forced:
                _logger.debug("Starting Sync download")
                self._is_syncing = True
                # Download
                job = DownloadJob()
                d = download(...)
                
                # Reset flags
                self._is_syncing = False
                self._force_sync = False
            if self.is_active:
                pass
                #time.sleep(self._check_sleep_time)

    
    def force_sync(self):
        self._force_sync = True

    @property
    def next_sync_time(self) -> datetime:
        return self._next_sync_time

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_outdated(self) -> bool:
        if TODO last_sync_time is None:
            return True
        return datetime.now(timezone.utc) >= self.next_sync_time

    @property
    def is_forced(self) -> bool:
        return self._force_sync

    @property
    def is_syncing(self) -> bool:
        return self._is_syncing

