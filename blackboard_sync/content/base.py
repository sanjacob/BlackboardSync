import os
from pathlib import Path
from datetime import datetime
from requests import Response

from concurrent.futures import ThreadPoolExecutor


class BStream:
    """Base class for content that can be downloaded as a byte stream."""
    CHUNK_SIZE = 1024

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   stream: Response,
                   modified: datetime | None = None) -> None:
        """Schedule the write operation."""

        def _write() -> None:
            with path.open("wb") as f:
                for chunk in stream.iter_content(chunk_size=self.CHUNK_SIZE):
                    f.write(chunk)

            set_mtime(path, modified)

        executor.submit(_write)


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
