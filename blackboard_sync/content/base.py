import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from requests import Response
from collections.abc import Callable

from concurrent.futures import ThreadPoolExecutor

from blackboard.exceptions import BBBadRequestError, BBForbiddenError

logger = logging.getLogger(__name__)


class BStream:
    """Base class for content that can be downloaded as a byte stream.

    The download is started by the worker thread that saves it, rather than
    when the content tree is built, so at most one connection per worker is
    open at a time. The connection is always closed afterwards.
    """
    CHUNK_SIZE = 1024

    def write_base(self, executor: ThreadPoolExecutor,
                   download: Callable[[], Response],
                   save: Callable[[Response], None], name: str) -> None:
        """Schedule `download`, then `save` with its response.

        A file the server refuses to send is logged and skipped, so it does
        not fail the rest of the sync.
        """

        def _download_and_save() -> None:
            try:
                stream = download()
            except (BBBadRequestError, BBForbiddenError):
                logger.warning(f"Could not download {name}", exc_info=True)
                return

            try:
                save(stream)
            finally:
                stream.close()

        executor.submit(_download_and_save)

    def save_stream(self, path: Path, stream: Response,
                    modified: datetime | None = None) -> None:
        """Write `stream` to `path`. Runs on the worker thread."""
        with path.open("wb") as f:
            for chunk in stream.iter_content(chunk_size=self.CHUNK_SIZE):
                f.write(chunk)

        mark_downloaded(path)
        set_mtime(path, modified)


class FStream:
    """Base class for content that can be written as text."""

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   body: str, modified: datetime | None = None) -> None:
        """Schedule the write operation."""

        def _write() -> None:
            with path.open('w', encoding='utf-8') as f:
                f.write(body)

            mark_downloaded(path)
            set_mtime(path, modified)

        executor.submit(_write)


def mark_downloaded(path: Path) -> None:
    """Mark `path` as downloaded from the internet, as browsers do.

    On Windows this writes the Mark of the Web (a Zone.Identifier stream
    for the Internet zone), so SmartScreen and Office's Protected View
    treat the file with the same care as a browser download. Must run
    before `set_mtime`, as writing the stream updates the file's time.

    macOS quarantines files the app creates through LSFileQuarantineEnabled
    in its Info.plist instead. Other platforms have no equivalent.
    """
    if sys.platform != 'win32':
        return

    try:
        with open(f"{path}:Zone.Identifier", 'w', encoding='utf-8') as f:
            f.write("[ZoneTransfer]\nZoneId=3\n")
    except OSError:
        # e.g. FAT32 drives and some network shares have no such streams
        logger.debug(f"Could not mark {path} as downloaded", exc_info=True)


def set_mtime(path: Path, modified: datetime | None) -> None:
    """Set the access and modification times of `path` to `modified`."""
    if modified is not None:
        timestamp = modified.timestamp()
        os.utime(path, (timestamp, timestamp))
