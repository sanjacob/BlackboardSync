from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBAttachment

from .base import BStream
from .api_path import BBContentPath


class Attachment(BStream):
    """A single Blackboard attachment obtained from the API"""

    def __init__(self, attachment: BBAttachment, api_path: BBContentPath,
                 session: BlackboardExtended):
        self.filename = attachment.fileName
        self.stream = session.download(attachment_id=attachment.id,
                                       **api_path._asdict())

    def write(self, path: Path, executor: ThreadPoolExecutor):
        super().write(path / self.filename, self.stream, executor)
