from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent

from .job import DownloadJob


class Other:
    """Content which we cannot handle yet, or at all."""

    def __init__(self, content: BBCourseContent, _, job: DownloadJob):
        pass

    def write(self, path: Path, executor: ThreadPoolExecutor):
        pass
