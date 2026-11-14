import platform
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.blackboard import BBCourseContent

from .base import FStream
from .job import DownloadJob
from .naming import safe_filename


class ExternalLink(FStream):
    """Creates a platform-aware internet shortcut."""

    def __init__(self, content: BBCourseContent, _: None,
                 job: DownloadJob) -> None:
        self.url = None

        if content.contentHandler is not None:
            self.url = content.contentHandler.url

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        if self.url is None:
            return

        if platform.system() in ["Windows", "Darwin"]:
            body = f"[InternetShortcut]\nURL={self.url}"
            suffix = ".url"
        else:
            body = self.create_unix_body(self.url)
            suffix = ".desktop"

        path = path / safe_filename(path.name, suffix)

        super().write_base(path, executor, body)

    def create_unix_body(self, url: str) -> str:
        return f"[Desktop Entry]\nIcon=text-html\nType=Link\nURL[$e]={url}"

    @property
    def create_dir(self) -> bool:
        return True
