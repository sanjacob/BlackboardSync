from pathlib import Path
from unittest import mock
from datetime import datetime, timezone

from blackboard.blackboard import (
    BBCourse,
    BBAttachment,
    BBAvailability,
    BBCourseContent,
    BBContentHandler,
    BBResourceType,
)

from blackboard_sync.executor import SyncExecutor
from blackboard_sync.content import Course
from blackboard_sync.content.base import BStream, FStream
from blackboard_sync.content.body import ContentBody
from blackboard_sync.content.externallink import ExternalLink
from blackboard_sync.content.webdav import last_modified


COURSE_TIME = datetime(2024, 9, 1, 9, 0, tzinfo=timezone.utc)
FOLDER_TIME = datetime(2024, 10, 2, 10, 30, tzinfo=timezone.utc)
FILE_TIME = datetime(2024, 11, 3, 14, 45, tzinfo=timezone.utc)
AVAILABLE = BBAvailability(available="Yes")


def run_now() -> mock.Mock:
    return mock.Mock(submit=lambda fn: fn())


def stream(data: bytes = b"data") -> mock.Mock:
    return mock.Mock(iter_content=lambda chunk_size: [data])


def mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def test_bstream_sets_mtime(tmp_path: Path) -> None:
    path = tmp_path / "file.bin"
    BStream().save_stream(path, stream(), FILE_TIME)
    assert mtime(path) == FILE_TIME


def test_fstream_sets_mtime(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    FStream().write_base(path, run_now(), "text", FILE_TIME)
    assert mtime(path) == FILE_TIME


def test_no_time_keeps_write_time(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    before = datetime.now(timezone.utc).timestamp()
    FStream().write_base(path, run_now(), "text")
    assert path.stat().st_mtime >= before - 1


def test_content_body_time(tmp_path: Path) -> None:
    content = BBCourseContent(id="_1_1", title="Week 1",
                              body="<p>Welcome</p>", modified=FILE_TIME)
    job = mock.Mock()
    job.session.instance_url = "https://example.com"

    ContentBody(content, None, job).write(tmp_path, run_now())

    [html] = tmp_path.glob("*.html")
    assert mtime(html) == FILE_TIME


def test_external_link_time(tmp_path: Path) -> None:
    handler = BBContentHandler(id=BBResourceType.ExternalLink,
                               url="https://example.com")
    content = BBCourseContent(id="_1_1", title="Link",
                              contentHandler=handler, modified=FILE_TIME)

    ExternalLink(content, None, mock.Mock()).write(tmp_path, run_now())

    [link] = tmp_path.iterdir()
    assert mtime(link) == FILE_TIME


def test_webdav_last_modified() -> None:
    def response(headers: dict[str, str]) -> mock.Mock:
        return mock.Mock(headers=headers)

    header = {"Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"}
    assert last_modified(response(header)) == FILE_TIME
    assert last_modified(response({"Last-Modified": "soon"})) is None
    assert last_modified(response({})) is None


def test_dir_times_applied_after_writes(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    missing = tmp_path / "never created"

    executor = SyncExecutor()
    executor.set_dir_mtime(folder, FOLDER_TIME)
    executor.set_dir_mtime(missing, FOLDER_TIME)
    executor.set_dir_mtime(tmp_path, None)

    # Creating a file in the folder would reset a time set too early
    executor.submit((folder / "new.txt").write_text, "text")
    executor.shutdown()
    executor.apply_dir_times()

    assert mtime(folder) == FOLDER_TIME
    assert not missing.exists()


def test_course_sync_times(tmp_path: Path) -> None:
    """Course, content folder and attachments all get Blackboard times."""
    document = BBCourseContent(
        id="_2_1", title="Slides", availability=AVAILABLE,
        contentHandler=BBContentHandler(id=BBResourceType.File),
        modified=FOLDER_TIME,
    )
    course = BBCourse(id="_1_1", name="MATH101 : Maths",
                      availability=AVAILABLE,
                      created=COURSE_TIME, modified=COURSE_TIME)
    attachments = [
        BBAttachment(id="_3_1", fileName="a.pdf", mimeType="application/pdf"),
        BBAttachment(id="_3_2", fileName="b.pdf", mimeType="application/pdf"),
    ]

    job = mock.Mock()
    job.has_changed.return_value = True
    job.session.fetch_contents.return_value = [document]
    job.session.fetch_file_attachments.return_value = attachments
    job.session.download.side_effect = lambda **_: stream()

    executor = SyncExecutor()
    Course(course, job).write(tmp_path, executor)
    executor.shutdown()
    executor.apply_dir_times()
    executor.raise_exceptions()

    course_dir = tmp_path / "2024" / "Maths"
    slides_dir = course_dir / "Slides"

    assert mtime(course_dir) == COURSE_TIME
    assert mtime(slides_dir) == FOLDER_TIME
    assert {p.name for p in slides_dir.iterdir()} == {"a.pdf", "b.pdf"}

    for pdf in slides_dir.iterdir():
        assert mtime(pdf) == FOLDER_TIME
