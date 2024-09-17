#!/usr/bin/env python3

"""
BlackboardDownload,
mass download all user content from Blackboard
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import logging
from pathlib import Path
from datetime import datetime, timezone

from blackboard.api_extended import BlackboardExtended
from blackboard.filters import BBMembershipFilter, BWFilter

from .executor import SyncExecutor
from .content.job import DownloadJob
from .content.course import Course


logger = logging.getLogger(__name__)


class BlackboardDownload:
    """Blackboard download job."""

    _last_downloaded = datetime.fromtimestamp(0, tz=timezone.utc)

    def __init__(self, sess: BlackboardExtended,
                 download_location: Path,
                 last_downloaded: datetime | None = None,
                 min_year: int | None = None):
        """BlackboardDownload constructor

        Download all files in blackboard recursively to download_location,
        only if they have been altered since specified datetime

        Keyword arguments:

        :param BlackboardExtended sess: UCLan BB user session
        :param (str / Path) download_location: Where files will be stored
        :param str last_downloaded: Files modified before are ignored
        :param min_year: Courses created before are ignored
        """

        self._sess = sess
        self._user_id = sess.user_id
        self._download_location = download_location
        self._min_year = min_year
        self.executor = SyncExecutor()
        self.cancelled = False

        if last_downloaded is not None:
            self._last_downloaded = last_downloaded

    def download(self) -> datetime | None:
        """Retrieve the user's courses, and start download of all contents

        :return: Datetime when method was called.
        """
        if self.cancelled:
            return None

        logger.info("Starting Blackboard content download")

        start_time = datetime.now(timezone.utc)

        if not self.download_location.exists():
            self.download_location.mkdir(parents=True)
            logger.info("Created download folder")

        logger.info("Fetching user memberships and courses")

        course_filter = BBMembershipFilter(min_year=self._min_year,
                                           data_sources=BWFilter())
        courses = self._sess.ex_fetch_courses(user_id=self.user_id,
                                              result_filter=course_filter)

        job = DownloadJob(session=self._sess,
                          last_downloaded=self._last_downloaded)

        for course in courses:
            if self.cancelled:
                break

            logger.info(f"Fetching user course <{course.id}>")

            Course(course, job).write(self.download_location, self.executor)

        logger.info("Shutting down download workers")

        self.executor.shutdown(wait=True, cancel_futures=self.cancelled)
        self.executor.raise_exceptions()

        return start_time if not self.cancelled else None

    def cancel(self) -> None:
        """Cancel the download job."""
        self.cancelled = True

    @property
    def download_location(self) -> Path:
        """The location where files will be downloaded to."""
        return self._download_location

    @property
    def user_id(self) -> str:
        """User ID used for API calls."""
        return self._user_id
