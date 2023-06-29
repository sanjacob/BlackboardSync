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
from getpass import getpass
from typing import Optional
from dateutil.parser import parse
from datetime import datetime, timezone
from pathvalidate import sanitize_filename
from concurrent.futures import ThreadPoolExecutor

from .blackboard import BlackboardSession, BBCourseContent, BBResourceType
from .webdav import ContentParser, Link, validate_webdav_response


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
        self._user_id = sess.username
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

    def _create_desktop_link(self, path: Path, url: str, comment: str = "") -> None:
        """Creates a platform-aware internet shortcut"""
        if platform.system() in ["Windows", "Darwin"]:
            contents = f"[InternetShortcut]\nURL={url}"
            path = path.with_suffix(".url")
        else:
            contents = f"[Desktop Entry]\nIcon=text-html\nType=Link\nURL[$e]={url}"

        with path.open("w") as f:
            f.write(contents)
            self.logger.info(f"Created internet link file at {path}")

    def _download_file(self, course_id: str, content_id: str, attachment_id: str, file_path: Path) -> None:
        """Get stream for blackboard file and download."""
        try:
            d_stream = self._sess.download(course_id=course_id,
                                       content_id=content_id,
                                       attachment_id=attachment_id)
            self._download_stream(d_stream, file_path)
        except RequestException as e:
            self.logger.warn(f"Error while downloading file {content_id}")

    def _download_webdav_file(self, link: str, file_path: Path) -> None:
        try:
            response = self._sess.download_webdav(webdav_url=link)
            if validate_webdav_response(response, link, self._sess.base_url):
                self._download_stream(response, file_path)
            else:
                self.logger.info(f"Not downloading webdav/ext file {link}")
        except RequestException as e:
            self.logger.warn(f"Error while downloading webdav/ext file {link}")


    def _download_stream(self, stream, file_path):
        """Generic stream download function."""
        with file_path.open("wb") as f:
            self.logger.info(f"Writing to {file_path}")
            for chunk in stream.iter_content(chunk_size=1024):
                f.write(chunk)

    def _handle_file(self, content: BBCourseContent, parent_path: Path,
                     course_id: str, depth: int = 0) -> None:
        """Download BBContent recursively, depending on filetype"""
        if self.cancelled:
            return

        res = content.contentHandler

        handler_id = res.id if res is not None else '?'
        self.logger.info(f"{'    ' * depth}{content.title}[{handler_id}]")

        body_path = parent_path
        file_path = Path(parent_path, content.title_path_safe)
        has_changed = True

        if content.modified is not None:
            has_changed = (content.modified >= self._last_downloaded)

        if res is None:
            pass

        elif res == BBResourceType.folder:
            try:
                body_path = file_path
                children = self._sess.fetch_content_children(course_id=course_id,
                                                             content_id=content.id)

                if children or content.body:
                    file_path.mkdir(exist_ok=True, parents=True)

                for child in children:
                    if child.contentHandler is not None:
                        self._handle_file(child, file_path, course_id, depth + 1)
            except ValueError:
                pass

        # Omit file if it hasn't been modified since last sync
        elif res in (BBResourceType.file, BBResourceType.document) and has_changed:
            attachments = []

            try:
                attachments = self._sess.fetch_file_attachments(course_id=course_id,
                                                                content_id=content.id)

            except RequestException:
                self.logger.warn(f"Error while getting attachments for {course_id}")

            if len(attachments) > 1:
                file_path.mkdir(exist_ok=True, parents=True)
                body_path = file_path

            for attachment in attachments:
                download_path = Path(body_path / attachment.fileName)
                if attachment.mimeType.startswith('video/'):
                    self.logger.info(f'Not downloading {attachment.fileName}')
                else:
                    if not self.cancelled and content.id is not None:
                        self.executor.submit(self._download_file,
                                             course_id, content.id,
                                             attachment.id, download_path)

        elif res == BBResourceType.externallink and has_changed:
            # Place link under folder of its own, in case it has a body
            file_path.mkdir(exist_ok=True, parents=True)
            link_path = file_path / content.title_path_safe
            if res.url is not None:
                self._create_desktop_link(link_path, res.url)

        elif not res.is_not_handled and has_changed:
            self.logger.warning(f"Not handled, {content.title}")

        # If item has body, write in markdown file
        if content.body and has_changed:
            file_path.mkdir(exist_ok=True, parents=True)

            # Parse content.body for more attachments
            parser = ContentParser(content.body, self._sess.base_url)

            for body_link in parser.links:
                safe_title = sanitize_filename(body_link.text, replacement_text='_')
                download_path = Path(file_path / safe_title)
                self.executor.submit(self._download_webdav_file, body_link.href, download_path)

            with Path(file_path, f"{content.title_path_safe}.html").open('w') as html_content:
                html_content.write(parser.body)

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
                self.logger.info(f"<{course.code}> - <{course.title}>")

                course_contents = self._sess.fetch_contents(course_id=course.id)

                if course_contents:
                    course_path = Path(self.download_location / str(ms.created.year) / course.title)

                for content in course_contents:

                    if self.cancelled:
                        break

                    self._handle_file(content, course_path, course.id, 1)
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

