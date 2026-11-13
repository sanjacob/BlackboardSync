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


import re
import json
import mimetypes
from pathlib import Path
from requests import Response
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import unquote
from typing import List, NamedTuple
from pathvalidate import sanitize_filename
from concurrent.futures import ThreadPoolExecutor

from .base import BStream
from .job import DownloadJob


# Matches filename="..." and the RFC 5987 filename*=UTF-8''... form
_DISPOSITION_FILENAME_RE = re.compile(
    r"filename\*?=(?:UTF-8'')?\"?([^\";]+)\"?", re.IGNORECASE
)


def filename_from_disposition(
    headers: CaseInsensitiveDict,
) -> str | None:
    """Extract the real filename from a Content-Disposition header.

    Blackboard WebDav links do not always embed the file's actual
    name in the URL (some are just opaque content ids), so the
    response header is the only reliable source for it.
    """
    disposition = headers.get('Content-Disposition', '')
    match = _DISPOSITION_FILENAME_RE.search(disposition)
    return unquote(match.group(1)) if match else None


def filename_from_bbfile(el: Tag) -> str | None:
    """Extract the real filename from Blackboard's own editor metadata.

    Links/images inserted through Blackboard's rich text editor
    carry a `data-bbfile` attribute with a JSON blob describing the
    original file (its real name, mimetype, etc). The URL itself is
    often just an opaque content id, so this is the only place the
    human-readable filename set in the Blackboard UI is available.
    """
    raw = el.get('data-bbfile')

    if not raw:
        return None

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None

    return data.get('linkName') or data.get('displayName')


class Link(NamedTuple):
    href: str
    text: str


class ContentParser:
    def __init__(self, body: str, base_url: str,
                 *, find_links: bool = True) -> None:
        soup = BeautifulSoup(body, 'html.parser')
        self._links = []

        if find_links:
            a = self._find_replace(soup, 'a', 'href', base_url)
            img = self._find_replace(soup, 'img', 'src', base_url)
            self._links = [*a, *img]

        self._body = str(soup)
        self._text = soup.text

    def _find_replace(self, soup: BeautifulSoup,
                      tag: str, attr: str, base_url: str) -> list[Link]:
        links = []

        for el in soup.find_all(tag):
            # Add link for later download
            uri = el.get(attr)

            if uri:
                # Prefer the real filename Blackboard's editor stores
                # in data-bbfile; the URL itself is often just an
                # opaque content id with no readable name in it.
                path = uri.split('?', 1)[0]
                url_filename = unquote(path.split('/')[-1])
                filename = filename_from_bbfile(el) or url_filename

                links.append(Link(href=uri, text=filename))

                # Replace for local instance
                if uri.startswith(base_url):
                    el[attr] = filename
        return links

    @property
    def links(self) -> List[Link]:
        return self._links

    @property
    def body(self) -> str:
        return self._body

    @property
    def text(self) -> str:
        return self._text


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
        self.stream = job.session.download_webdav(webdav_url=link.href)

        filename = filename_from_disposition(self.stream.headers) or link.text
        self.title = sanitize_filename(filename, replacement_text="_")

        content_type = self.stream.headers.get('Content-Type', 'text/plain')
        # Only guess an extension if the real filename didn't come
        # with one already (e.g. link.text with no suffix at all).
        self.extension = (None if Path(self.title).suffix
                          else mimetypes.guess_extension(content_type))
        self.valid = validate_webdav_response(self.stream, link.href,
                                              job.session.instance_url)

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        if self.valid:
            path = Path(path, self.title)

            if self.extension:
                path = path.with_suffix(self.extension)

            super().write_base(path, executor, self.stream)
