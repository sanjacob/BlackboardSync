import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent

from .job import DownloadJob

logger = logging.getLogger(__name__)


class Unhandled:
    """Content which we cannot handle yet, or at all."""

    def __init__(self, content: BBCourseContent, _, job: DownloadJob):
        logger.info(f"{content.title} not supported")

    def write(self, path: Path, executor: ThreadPoolExecutor):
        pass

    @property
    def create_dir(self) -> bool:
        return False
