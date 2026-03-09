from pathlib import Path
from requests import Response

from concurrent.futures import ThreadPoolExecutor


class BStream:
    """Base class for content that can be downloaded as a byte stream."""
    CHUNK_SIZE = 1024

    @staticmethod
    def _write_stream(path: Path, stream: Response,
                      chunk_size: int = CHUNK_SIZE) -> None:
        """Write a streaming response to disk, always closing the stream."""
        try:
            with path.open("wb") as f:
                for chunk in stream.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
        finally:
            stream.close()

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   stream: Response) -> None:
        """Schedule the write operation."""
        executor.submit(BStream._write_stream, path, stream, self.CHUNK_SIZE)


class FStream:
    """Base class for content that can be written as text."""

    def write_base(self, path: Path, executor: ThreadPoolExecutor,
                   body: str) -> None:
        """Schedule the write operation."""

        def _write() -> None:
            with path.open('w', encoding='utf-8') as f:
                f.write(body)

        executor.submit(_write)
