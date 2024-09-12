from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.blackboard import BBCourseContent

from .api_path import BBContentPath
from .job import DownloadJob
from . import content


class Folder:
    """Content of type `x-bb-folder`."""

    def __init__(self, _: BBCourseContent, api_path: BBContentPath,
                 job: DownloadJob) -> None:
        self.children = []
        course_id = api_path['course_id']

        for child in job.session.fetch_content_children(**api_path):
            child_path = BBContentPath(content_id=child.id,
                                       course_id=course_id)
            self.children.append(content.Content(child, child_path, job))

    def write(self, path: Path, executor: ThreadPoolExecutor) -> None:
        if self.children:
            path.mkdir(exist_ok=True, parents=True)

        for child in self.children:
            child.write(path, executor)

    @property
    def create_dir(self) -> bool:
        return False
