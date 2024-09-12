import uuid

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
        self.filename = attachment.fileName
        self.stream = job.session.download(attachment_id=attachment.id,
                                           **api_path)

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        filename = self.filename or str(uuid.uuid1())
        super().write_base(path / filename, executor, self.stream)
