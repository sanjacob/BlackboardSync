import uuid
import mimetypes

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.blackboard import BBAttachment

from .base import BStream
from .api_path import BBContentPath
from .job import DownloadJob


class Attachment(BStream):
    """File attached to a content."""

    def __init__(self, attachment: BBAttachment, api_path: BBContentPath,
                 job: DownloadJob):
        filename = attachment.fileName or str(uuid.uuid1())
        name_ext = '.' + filename.split('.')[-1]

        # Guess extension based on content
        mime = attachment.mimeType or 'text/plain'
        possible_ext = mimetypes.guess_all_extensions(mime, strict=False)

        if name_ext in possible_ext:
            self.filename = filename
        else:
            real_ext = possible_ext[0] if possible_ext else '.txt'
            self.filename = filename + real_ext

        # Store download parameters; defer opening the connection until write()
        self._session = job.session
        self._attachment_id = attachment.id
        self._api_path = api_path

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        session = self._session
        attachment_id = self._attachment_id
        api_path = self._api_path
        filepath = path / self.filename

        def _download_and_write() -> None:
            stream = session.download(attachment_id=attachment_id, **api_path)
            BStream._write_stream(filepath, stream)

        executor.submit(_download_and_write)
