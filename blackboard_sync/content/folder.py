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

        # Blackboard sometimes models a folder's single "page" as a
        # separate content item sharing the folder's own title. If
        # left alone, that doubles up the folder on disk (e.g.
        # "Lecture notes/Lecture notes/..."). When this folder has
        # exactly one child with the same title, skip the extra
        # nesting level and write the child directly into this
        # folder's own directory.
        only_child = self.children[0] if len(self.children) == 1 else None

        if (only_child is not None and not only_child.ignore
                and only_child.title == path.name):
            only_child.write(path.parent, executor)
            return

        for child in self.children:
            child.write(path, executor)

    @property
    def create_dir(self) -> bool:
        return False
