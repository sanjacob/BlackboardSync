from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent

from .api_path import BBContentPath
from .job import DownloadJob
from .content import Content


class Folder:
    """Content of type `x-bb-folder`."""

    def __init__(self, content: BBCourseContent, api_path: BBContentPath,
                 job: DownloadJob):
        self.children = []
        course_id = api_path.get('course_id')

        for child in job.session.fetch_content_children(**api_path):
            if child.contentHandler is not None:
                self.children.append(
                    Content(child, {'content_id': child.id, 'course_id': course_id}, job)
                )

    def write(self, path: Path, executor: ThreadPoolExecutor):
        if self.children:
            path.mkdir(exist_ok=True, parents=True)

        for child in self.children:
            child.write(path, executor)

    @property
    def create_dir(self) -> bool:
        return False
