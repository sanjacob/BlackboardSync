import os
import re
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, cast
from requests import Response, RequestException
from requests.exceptions import ChunkedEncodingError, ConnectionError
from collections.abc import Callable, Iterator

from concurrent.futures import ThreadPoolExecutor

from blackboard.exceptions import BBBadRequestError, BBForbiddenError

from ..executor import SyncExecutor

logger = logging.getLogger(__name__)

# Raised while reading a response body when the connection breaks part way
# (e.g. IncompleteRead, a reset or a read timeout). requests.SSLError is a
# ConnectionError too. The bytes received before the error are still valid.
INTERRUPTED = (ChunkedEncodingError, ConnectionError)


class ResumeError(RequestException):
    """The download cannot be continued from where it stopped."""


class ResumableResponse:
    """A streamed response that continues where it stopped if cut short.

    If reading the body fails part way, the file is requested again from
    the first missing byte (`Range`, with `If-Range` so that a changed
    file is never stitched together from two versions) and reading
    carries on. A server that
    ignores the range and sends the whole file again is also handled, by
    skipping the bytes already received. It gives up after `max_retries`
    failed attempts in a row; any attempt that receives data resets the
    count, so a slow but progressing download is never abandoned.

    Everything other than reading (status, headers, ...) comes from the
    first response. `on_interrupt` is called on every network failure,
    including those that are recovered from.
    """

    def __init__(self, response: Response, download: Callable[..., Response],
                 max_retries: int, retry_delay: float,
                 on_interrupt: Callable[[], None] | None = None) -> None:
        self._first = response
        self._on_interrupt = on_interrupt
        self._current = response
        self._download = download
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # A compressed body's byte positions differ from the decoded data we
        # count, and some servers say they cannot serve ranges at all. Then,
        # or once a range request fails, resume by fetching the whole file
        # again and skipping the bytes already saved.
        self._ranges = (
            not response.headers.get('Content-Encoding')
            and response.headers.get('Accept-Ranges', '').lower() != 'none'
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._first, name)

    def close(self) -> None:
        self._current.close()

        if self._current is not self._first:
            self._first.close()

    def iter_content(self, chunk_size: int = 1) -> Iterator[bytes]:
        received = 0
        failures = 0
        skip = 0

        while True:
            received_before = received

            try:
                if failures:
                    skip = self._reopen(received)

                for chunk in self._current.iter_content(chunk_size=chunk_size):
                    if skip:
                        dropped = min(skip, len(chunk))
                        chunk, skip = chunk[dropped:], skip - dropped

                    received += len(chunk)

                    if chunk:
                        yield chunk

                if skip:
                    raise ResumeError("Resent file is shorter than before")

                return
            except INTERRUPTED:
                if self._on_interrupt is not None:
                    self._on_interrupt()

                if not skip and str(received) == _length(self._first):
                    return  # every byte arrived before the connection broke

                failures = 1 if received > received_before else failures + 1

                if failures > self.max_retries:
                    raise

                logger.warning(f"Download interrupted after {received} bytes, "
                               f"retrying ({failures}/{self.max_retries})")
                time.sleep(self.retry_delay * failures)

    def _reopen(self, offset: int) -> int:
        """Request the file again from `offset`.

        Returns how many bytes of the new response to skip.
        """
        self._current.close()
        headers = {}

        if self._ranges and offset:
            headers['Range'] = f"bytes={offset}-"

            # Only continue if the file is unchanged; otherwise the server
            # sends the new version in full (and _changed() rejects it)
            if validator := _validator(self._first):
                headers['If-Range'] = validator

        self._current = self._download(headers=headers)
        status = self._current.status_code

        if status in (200, 206) and _changed(self._first, self._current):
            raise ResumeError("File changed since the download started")

        if status == 206 and headers:
            start, total = _content_range(self._current)

            if total is not None and _length(self._first) not in (None, total):
                raise ResumeError("File changed since the download started")
            if start == offset:
                return 0

            # The server got the range wrong: stop trusting it with ranges
            return self._without_ranges(offset)

        if status in (416, 501) and headers:
            # Range not satisfiable / not implemented
            return self._without_ranges(offset)

        if status == 200:
            if headers:
                # Asked for a range but got the whole file: unsupported
                self._ranges = False

            if _length(self._current) != _length(self._first):
                raise ResumeError("File changed since the download started")
            return offset

        # Anything else (e.g. a 503) is retried like a broken connection
        raise ConnectionError(f"Server answered {status} when resuming")

    def _without_ranges(self, offset: int) -> int:
        logger.info("Server cannot resume with ranges, downloading again")
        self._ranges = False
        return self._reopen(offset)


def _validator(response: Response) -> str | None:
    """A strong ETag, or else Last-Modified, to identify this version."""
    etag = response.headers.get('ETag')

    if etag and not etag.startswith('W/'):
        return etag
    return response.headers.get('Last-Modified')


def _changed(first: Response, later: Response) -> bool:
    """True if the server identifies `later` as a different version."""
    for header in ('ETag', 'Last-Modified'):
        before, after = first.headers.get(header), later.headers.get(header)

        if before and after:
            return bool(before != after)
    return False


def _content_range(response: Response) -> tuple[int | None, str | None]:
    """Start and total size from a `Content-Range: bytes a-b/total` header."""
    content_range = response.headers.get('Content-Range', '')
    match = re.match(r"bytes (\d+)-\d+/(\d+|\*)", content_range)

    if not match:
        return None, None

    total = match.group(2)
    return int(match.group(1)), None if total == '*' else total


def _length(response: Response) -> str | None:
    if response.headers.get('Content-Encoding'):
        return None
    return response.headers.get('Content-Length')


class BStream:
    """Base class for content that can be downloaded as a byte stream.

    The download is started by the worker thread that saves it, rather than
    when the content tree is built, so at most one connection per worker is
    open at a time. The connection is always closed afterwards.
    """
    CHUNK_SIZE = 1024
    # Attempts in a row without progress before an interrupted download
    # is abandoned, and the base delay (seconds) between them
    MAX_RETRIES = 5
    RETRY_DELAY = 2.0

    def write_base(self, executor: ThreadPoolExecutor,
                   download: Callable[..., Response],
                   save: Callable[[Response], None], name: str) -> None:
        """Schedule `download`, then `save` with its response.

        A file the server refuses to send is logged and skipped, so it does
        not fail the rest of the sync. If the connection breaks while the
        file is being saved, the download resumes where it stopped.
        `download` must accept a `headers` keyword argument for that.
        """

        def _download_and_save() -> None:
            try:
                response = download()
            except (BBBadRequestError, BBForbiddenError):
                logger.warning(f"Could not download {name}", exc_info=True)
                return

            on_interrupt = None

            if isinstance(executor, SyncExecutor):
                on_interrupt = executor.report_network_error

            stream = ResumableResponse(response, download,
                                       self.MAX_RETRIES, self.RETRY_DELAY,
                                       on_interrupt)

            try:
                save(cast(Response, stream))
            finally:
                stream.close()

        executor.submit(_download_and_save)

    def save_stream(self, path: Path, stream: Response,
                    modified: datetime | None = None) -> None:
        """Write `stream` to `path`. Runs on the worker thread."""
        with path.open("wb") as f:
            for chunk in stream.iter_content(chunk_size=self.CHUNK_SIZE):
                f.write(chunk)

        set_mtime(path, modified)


class FStream:
    """Base class for content that can be written as text."""

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   body: str, modified: datetime | None = None) -> None:
        """Schedule the write operation."""

        def _write() -> None:
            with path.open('w', encoding='utf-8') as f:
                f.write(body)

            set_mtime(path, modified)

        executor.submit(_write)


def set_mtime(path: Path, modified: datetime | None) -> None:
    """Set the access and modification times of `path` to `modified`."""
    if modified is not None:
        timestamp = modified.timestamp()
        os.utime(path, (timestamp, timestamp))
