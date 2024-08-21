import platform
from pathlib import Path


def windows_safe_path(path):
    UNC_PREFIX = u'\\\\?\\'

    if platform.system() == "Windows":
        return Path(UNC_PREFIX + str(path))
    return path


class BStream:
    """Base class for content that can be downloaded as a byte stream."""
    CHUNK_SIZE = 1024

    def write(self, path, stream, executor) -> None:
        """Schedule the write operation."""

        path = windows_safe_path(path)

        def _write():
            with path.open("wb") as f:
                for chunk in stream.iter_content(chunk_size=self.CHUNK_SIZE):
                    f.write(chunk)

        executor.submit(_write)


class FStream:
    """Base class for content that can be written as text."""

    def write(self, path, body, executor) -> None:
        """Schedule the write operation."""

        path = windows_safe_path(path)

        def _write():
            with path.open('w', encoding='utf-8') as f:
                f.write(body)

        executor.submit(_write)
