import platform
from pathlib import Path
from requests import Response

from concurrent.futures import ThreadPoolExecutor


def windows_safe_path(path: Path) -> Path:
    UNC_PREFIX = u'\\\\?\\'

    if platform.system() == "Windows":
        return Path(UNC_PREFIX + str(path))
    return path


class BStream:
    """Base class for content that can be downloaded as a byte stream."""
    CHUNK_SIZE = 1024

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   stream: Response) -> None:
        """Schedule the write operation."""

        path = windows_safe_path(path)

        def _write() -> None:
            with path.open("wb") as f:
                for chunk in stream.iter_content(chunk_size=self.CHUNK_SIZE):
                    f.write(chunk)

        executor.submit(_write)


class FStream:
    """Base class for content that can be written as text."""

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   body: str) -> None:
        """Schedule the write operation."""

        path = windows_safe_path(path)

        def _write() -> None:
            with path.open('w', encoding='utf-8') as f:
                f.write(body)

        executor.submit(_write)
