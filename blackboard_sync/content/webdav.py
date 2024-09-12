"""
Parse an html to look for links
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


import mimetypes
from pathlib import Path
from requests import Response
from bs4 import BeautifulSoup
from typing import List, NamedTuple
from pathvalidate import sanitize_filename
from concurrent.futures import ThreadPoolExecutor

from .base import BStream
from .job import DownloadJob


class Link(NamedTuple):
    href: str
    text: str


class ContentParser:
    def __init__(self, body: str, base_url: str) -> None:
        links = []
        soup = BeautifulSoup(body, 'html.parser')

        for link in soup.find_all('a'):
            # Add link for later download
            links.append(Link(href=link.get('href'), text=link.text.strip()))

            # Replace for local instance
            if link['href'].startswith(base_url):
                filename = link.text.strip()
                link['href'] = filename
                link.string = filename
        self._links = links
        self.soup = soup

    @property
    def links(self) -> List[Link]:
        return self._links

    @property
    def body(self) -> str:
        return str(self.soup)


def validate_webdav_response(response: Response,
                             link: str, base_url: str) -> bool:
    if response.status_code == 200:
        h = response.headers
        content_type = h.get('Content-Type', '')
        content_len = int(h.get('Content-Length', 0))

        # TODO: feature: select mime types
        len_limit = 1024 * 1024 * 20  # 20 MB

        filters = [
            link.startswith(base_url),
            'video' not in content_type,
            content_len < len_limit
        ]

        return all(filters)
    return False


class WebDavFile(BStream):
    """A Blackboard WebDav file which can be downloaded directly"""
    def __init__(self, link: Link, job: DownloadJob) -> None:
        self.title = sanitize_filename(link.text, replacement_text="_")
        self.stream = job.session.download_webdav(webdav_url=link.href)
        content_type = self.stream.headers.get('Content-Type', 'text/plain')
        self.extension = mimetypes.guess_extension(content_type)
        self.valid = validate_webdav_response(self.stream, link.href,
                                              job.session.instance_url)

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        if self.valid:
            path = Path(path, self.title)

            if self.extension:
                path = path.with_suffix(self.extension)

            super().write_base(path, executor, self.stream)
