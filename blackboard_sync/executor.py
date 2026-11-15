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

import os
from typing import Any
from pathlib import Path
from datetime import datetime
from collections.abc import Callable

from concurrent.futures import ThreadPoolExecutor, Future
from concurrent.futures import wait as wait_futures


class SyncExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers: int | None = None) -> None:
        super().__init__(max_workers)
        self.futures: list[Future[Any]] = []
        self.dir_times: dict[Path, datetime] = {}

    def submit(self, fn: Callable[..., Any], /,
               *args: Any, **kwargs: Any) -> Future[Any]:
        future = super().submit(fn, *args, **kwargs)
        self.futures.append(future)
        return future

    def shutdown(self, wait: bool = True, *,
                 cancel_futures: bool = False) -> None:
        super().shutdown(wait, cancel_futures=cancel_futures)

    def raise_exceptions(self, timeout: int | None = None) -> None:
        done, not_done = wait_futures(self.futures, timeout)

        for future in done:
            future.result()

    def set_dir_mtime(self, path: Path, modified: datetime | None) -> None:
        """Set the modification time of directory `path` after shutdown.

        Writing files into a directory updates its modification time, so
        directory times can only be applied once every write has finished.
        """
        if modified is not None:
            self.dir_times[path] = modified

    def apply_dir_times(self) -> None:
        """Apply the times recorded by `set_dir_mtime`.

        Must be called after `shutdown`. Directories that were never
        created (e.g. nothing in them was downloaded) are skipped.
        """
        for path, modified in self.dir_times.items():
            if path.is_dir():
                timestamp = modified.timestamp()
                os.utime(path, (timestamp, timestamp))

        self.dir_times.clear()
