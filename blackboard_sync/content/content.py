import logging
from pathlib import Path
from json import JSONDecodeError
from requests import RequestException
from concurrent.futures import ThreadPoolExecutor

from blackboard.api_extended import BlackboardExtended
from blackboard.blackboard import BBCourseContent, BBResourceType

from . import folder, document, externallink, body, other

from .api_path import BBContentPath
from .job import DownloadJob

logger = logging.getLogger(__name__)


class Content:
    """Content factory for all types."""

    def __init__(self, content: BBCourseContent, api_path: BBContentPath,
                 job: DownloadJob):

        logger.info(f"{content.title}[{content.contentHandler}]")
        self.ignore = False

        if not (job.has_changed(content.modified) or content.hasChildren):
            self.ignore = True
            return

        course_id = api_path.get('course_id')

        Handler = Content.get_handler(content.contentHandler)
        api_path = {'course_id': course_id, 'content_id': content.id}

        self.title = content.title_path_safe
        self.body = None

        try:
            self.handler = Handler(content, api_path, job)
        except (RequestException, JSONDecodeError):
            logger.exception(f"Error while preparing {child_path}")

        if content.body:
            self.body = body.ContentBody(content, None, job)

    def write(self, path: Path, executor: ThreadPoolExecutor):
        if self.ignore:
            return

        # Build nested path with content title
        path = path / self.title

        if self.handler.create_dir or self.body:
            path.mkdir(exist_ok=True, parents=True)

        self.handler.write(path, executor)

        if self.body is not None:
            self.body.write(path, executor)

    @staticmethod
    def get_handler(content_handler):
        match content_handler:
            case BBResourceType.Folder:
                return folder.Folder
            case BBResourceType.File | BBResourceType.Document:
                return document.Document
            case BBResourceType.ExternalLink:
                return externallink.ExternalLink
            case _:
                return other.Other
