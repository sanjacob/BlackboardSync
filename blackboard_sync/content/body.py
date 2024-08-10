from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent

from .base import FStream
from .webdav import WebDavFile, ContentParser

from .job import DownloadJob


class ContentBody(FStream):
    """Process the content body to find WebDav files."""

    def __init__(self, content: BBCourseContent, _,
                 job: DownloadJob):
        parser = ContentParser(content.body, job.session.instance_url)
        self.body = parser.body
        self.children = [WebDavFile(ln, job) for ln in parser.links]

    def write(self, path: Path, executor: ThreadPoolExecutor):
        super().write(path / f"{path.stem}.html", self.body, executor)

        for child in self.children:
            child.write(path, executor)
