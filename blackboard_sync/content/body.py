from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.blackboard import BBCourseContent

from .base import FStream
from .webdav import WebDavFile, ContentParser

from .job import DownloadJob


class ContentBody(FStream):
    """Process the content body to find WebDav files."""

    def __init__(self, content: BBCourseContent, _: None,
                 job: DownloadJob) -> None:
        parser = ContentParser(content.body or "", job.session.instance_url)
        self.body = parser.body
        self.children = [WebDavFile(ln, job) for ln in parser.links]

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        super().write_base(path / f"{path.stem}.html", executor, self.body)

        for child in self.children:
            child.write(path, executor)
