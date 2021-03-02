#!/usr/bin/env python3

"""
BlackboardDownload,
mass download all user content from Blackboard

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

import logging
import platform
from pathlib import Path
from getpass import getpass
from dateutil.parser import parse
from datetime import datetime, timezone

from blackboard.api import BlackboardSession
from blackboard.blackboard import (BBCourse, BBMembership, BBAttachment,
                                   BBCourseContent, BBContentChild, SanitisePath)


class BlackboardDownload:
    _last_downloaded = datetime.fromtimestamp(0, tz=timezone.utc)
    _data_source = "_21_1"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())

    def __init__(self, sess: BlackboardSession, download_location,
                 last_downloaded: datetime = None):
        """BlackboardDownload constructor

        Download all files in blackboard recursively to download_location,
        only if they have been altered since specified datetime

        Keyword arguments:

        :param BlackboardSession sess: UCLan BB user session
        :param (str / Path) download_location: Where files will be stored
        :param str last_downloaded: Files modified before this will not be downloaded
        """

        self._sess = sess
        self._user_id = sess.username
        self._download_location = download_location
        self._files_processed = 0

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

    def _handle_file(self, content: BBCourseContent, parent_path,
                     course_id: str, depth: int = 0) -> None:
        """Download BBContent recursively, depending on filetype"""
        self.logger.info(f"{'    ' * depth}{content.title}[{content.contentHandler.id}]")

        type = content.contentHandler
        body_path = parent_path
        file_path = Path(parent_path, content.title_safe)
        has_changed = (content.modifiedDT >= self._last_downloaded)

        if type.isFolder:
            try:
                body_path = file_path
                children = self._sess.fetch_content_children(course_id=course_id,
                                                             content_id=content.id)

                if children or content.body:
                    file_path.mkdir(exist_ok=True, parents=True)

                for child in children:
                    self._handle_file(BBContentChild(**child), file_path, course_id, depth + 1)
            except ValueError:
                pass

        # Omit file if it hasn't been modified since last sync
        elif (type.isFile or type.isDocument) and has_changed:
            attachments = self._sess.fetch_file_attachments(course_id=course_id,
                                                            content_id=content.id)

            if len(attachments) > 1:
                file_path.mkdir(exist_ok=True, parents=True)
                body_path = file_path

            for attachment in [BBAttachment(**a) for a in attachments]:
                d_stream = self._sess.download(course_id=course_id,
                                               content_id=content.id,
                                               attachment_id=attachment.id)
                with Path(body_path / attachment.fileName).open("wb") as f:
                    self.logger.info(f"Writing to {attachment.fileName}")
                    for chunk in d_stream.iter_content(chunk_size=128):
                        f.write(chunk)

        elif type.isExternalLink and has_changed:
            self._create_desktop_link(file_path, type.url)

        elif not type.isNotHandled and has_changed:
            self.logger.warning(f"Not handled, {content.title}")

        # If item has body, write in markdown file
        if content.body and has_changed:
            with Path(body_path, f"{content.title_safe}.md").open('w') as md:
                md.write(content.body)

        if not type.isFolder and has_changed:
            self._files_processed += 1

    def download(self) -> datetime:
        """Retrieve the user's courses, and start download of all contents"""
        start_time = datetime.now(timezone.utc)

        self.logger.info("Fetching user memberships")
        all_memberships = self._sess.fetch_user_memberships(user_id=self.user_id,
                                                            dataSourceId=self._data_source)

        memberships = [BBMembership(**memb) for memb in all_memberships]

        for ms in memberships:
            self.logger.debug("Fetching course")
            course = BBCourse(**self._sess.fetch_courses(course_id=ms.courseId))

            code_split = course.name.split(' : ', 1)
            name_split = code_split[-1].split(',')
            module_name = SanitisePath.get_path(name_split[0])

            self.logger.info(f"<{code_split[0]}> - <{name_split[0]}>")

            course_contents = self._sess.fetch_contents(course_id=course.id)

            if course_contents:
                course_path = Path(self.download_location / ms.created[:4] / module_name)

            for content in (BBCourseContent(**content) for content in course_contents):
                self._handle_file(content, course_path, course.id, 1)

        return start_time

    @property
    def download_location(self) -> str:
        return self._download_location

    @property
    def data_source(self) -> str:
        return self._data_source

    @data_source.setter
    def data_source(self, source: str):
        self._data_source = source

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def files_processed(self) -> int:
        return self._files_processed


def configure() -> BlackboardSession:
    authorized = False
    sess = None

    while not authorized:
        username = input("Enter your UCLan mail: ")
        password = getpass("Enter your password: ")

        placeholder_pass = '*' * len(password)

        save = input(f"Use login configuration {username}: {placeholder_pass}? [Y/n] ")

        if save.lower() != "n":
            try:
                sess = BlackboardSession(username, password)
            except ValueError:
                print("Login parameters are incorrect, try again")
            else:
                authorized = True
        print()

    return sess


def main():
    sess = configure()
    last_downloaded = input("Download all files modified since: ")
    new_download = BlackboardDownload(sess, 'sync', parse(last_downloaded))
    new_download.download()


if __name__ == '__main__':
    main()
