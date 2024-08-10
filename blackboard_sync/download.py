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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
import platform
from requests.exceptions import RequestException
from pathlib import Path
from typing import Optional
from dateutil.parser import parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from blackboard.api import BlackboardSession
from blackboard.blackboard import BBCourseContent, BBResourceType
from .content import ExternalLink, ContentBody, Document, Folder, Content
from .content import BBContentPath
from .content.job import DownloadJob
from .content.course import Course


class BlackboardDownload:
    """Blackboard download job."""

    _last_downloaded = datetime.fromtimestamp(0, tz=timezone.utc)

    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging.StreamHandler())

    def __init__(self, sess: BlackboardSession,
                 download_location: Path,
                 last_downloaded: Optional[datetime] = None,
                 data_sources: list[str] = [],
                 min_year: Optional[int] = None):
        """BlackboardDownload constructor

        Download all files in blackboard recursively to download_location,
        only if they have been altered since specified datetime

        Keyword arguments:

        :param BlackboardSession sess: UCLan BB user session
        :param (str / Path) download_location: Where files will be stored
        :param str last_downloaded: Files modified before this will not be downloaded
        :param data_sources: List of valid data sources
        :param min_year: Only courses created on or after this year will be downloaded
        """

        self._sess = sess
        self._user_id = sess.user_id
        self._download_location = download_location
        self._data_sources = data_sources
        self._min_year = min_year
        self._files_processed = 0
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.cancelled = False

        if last_downloaded is not None:
            self._last_downloaded = last_downloaded

        if not self.download_location.exists():
            self.download_location.mkdir(parents=True)
            self.logger.info("Created download folder")

    def download(self) -> Optional[datetime]:
        """Retrieve the user's courses, and start download of all contents

        :return: Datetime when method was called.
        """
        if self.cancelled:
            return None

        start_time = datetime.now(timezone.utc)

        self.logger.info("Fetching user memberships")

        memberships = self._sess.fetch_user_memberships(user_id=self.user_id)

        # Filter courses by data source
        if self._data_sources:
            memberships = [m for m in memberships if m.dataSourceId in self._data_sources]

        # Filter courses by creation year
        if self._min_year is not None:
            memberships = [m for m in memberships if m.created.year >= self._min_year]

        job = DownloadJob(session=self._sess, last_downloaded=self._last_downloaded)

        for ms in memberships:
            if self.cancelled:
                break

            private = False
            self.logger.debug("Fetching course")
            try:
                course = self._sess.fetch_courses(course_id=ms.courseId)
            except ValueError as e:
                if not (private := (str(e) == 'Private course')):
                    raise e

            if not private:
                handler = Course(course, job)
                handler.write(self.download_location, self.executor)
        self.executor.shutdown(wait=True, cancel_futures=self.cancelled)

        if self.cancelled:
            return None
        return start_time

    def cancel(self) -> None:
        """Cancel the download job."""
        self.cancelled = True

    @property
    def download_location(self) -> Path:
        """The location where files will be downloaded to."""
        return self._download_location

    @property
    def data_sources(self) -> list[str]:
        """Filter for courses."""
        return self._data_sources

    @data_sources.setter
    def data_sources(self, sources: list[str]) -> None:
        self._data_sources = sources

    @property
    def user_id(self) -> str:
        """User ID used for API calls."""
        return self._user_id

    @property
    def files_processed(self) -> int:
        """Number of files that have been downloaded."""
        return self._files_processed

    @property
    def logger(self) -> logging.Logger:
        """Logger for BlackboardDownload, set at level DEBUG."""
        return self._logger

