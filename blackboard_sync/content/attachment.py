import uuid
import mimetypes

from functools import partial

from pathlib import Path
from datetime import datetime
from requests import Response
from concurrent.futures import ThreadPoolExecutor

from blackboard.blackboard import BBAttachment

from .base import BStream
from .naming import safe_filename, split_extension
from .api_path import BBContentPath
from .job import DownloadJob


class Attachment(BStream):
    """File attached to a content."""

    def __init__(self, attachment: BBAttachment, api_path: BBContentPath,
                 job: DownloadJob, modified: datetime | None = None):
        self.modified = modified
        filename = attachment.fileName or str(uuid.uuid1())
        stem, ext = split_extension(filename)

        # Keep the uploaded name; only guess an extension if it has none
        if not ext:
            mime = attachment.mimeType or 'text/plain'
            ext = mimetypes.guess_extension(mime, strict=False) or '.txt'

        self.filename = safe_filename(stem, ext)

        # Not downloaded yet: the worker that saves the file opens it
        self._download = partial(job.session.download,
                                 attachment_id=attachment.id, **api_path)

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        filepath = path / self.filename

        def save(stream: Response) -> None:
            self.save_stream(filepath, stream, self.modified)

        super().write_base(executor, self._download, save, self.filename)
