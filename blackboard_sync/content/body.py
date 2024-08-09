from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent

from .base import FStream
from .webdav import WebDavFile, ContentParser


class ContentBody(FStream):
    """Process the content body to find WebDav files."""

    def __init__(self, content: BBCourseContent, _,
                 session: BlackboardExtended):
        parser = ContentParser(content.body, session.url)
        self.body = parser.body
        self.children = [WebDavFile(ln, session) for ln in parser.links]

    def write(self, path: Path, executor: ThreadPoolExecutor):
        super().write(path / f"{path.stem}.html", self.body, executor)

        for child in self.children:
            child.write(path, executor)
