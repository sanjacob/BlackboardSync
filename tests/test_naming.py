from pathlib import Path
from unittest import mock

from hypothesis import given, strategies as st

from blackboard.blackboard import BBAttachment, BBCourse, BBAvailability

from blackboard_sync.content import Course
from blackboard_sync.content.attachment import Attachment
from blackboard_sync.content.externallink import ExternalLink
from blackboard_sync.content.webdav import WebDavFile
from blackboard_sync.content.naming import safe_filename, MAX_NAME_BYTES


LONG_TITLE = "Lecture notes " * 30  # 420 characters
SUFFIXES = ["", ".html", ".url", ".desktop", ".pdf"]


def run_now() -> mock.Mock:
    return mock.Mock(submit=lambda fn: fn())


def stream(data: bytes = b"data") -> mock.Mock:
    return mock.Mock(iter_content=lambda chunk_size: [data])


@given(st.text(), st.sampled_from(SUFFIXES))
def test_safe_filename_fits(name: str, suffix: str) -> None:
    result = safe_filename(name, suffix)
    assert len(result.encode()) <= MAX_NAME_BYTES
    assert result.endswith(suffix)
    assert "/" not in result and "\0" not in result
    assert result != suffix


def test_safe_filename_keeps_valid_names() -> None:
    assert safe_filename("Week 1 notes", ".pdf") == "Week 1 notes.pdf"
    assert safe_filename("Week 1 notes") == "Week 1 notes"


def test_safe_filename_truncates_stem_not_suffix() -> None:
    result = safe_filename("a" * 300, ".desktop")
    assert result == "a" * (MAX_NAME_BYTES - len(".desktop")) + ".desktop"


def test_safe_filename_counts_bytes() -> None:
    result = safe_filename("é" * 300, ".html")
    assert result.endswith(".html")
    assert len(result.encode()) <= MAX_NAME_BYTES


def test_safe_filename_separators_and_fallback() -> None:
    assert safe_filename("Maths I/II") == "Maths I_II"
    assert safe_filename("") == "Untitled"
    assert safe_filename("", fallback="Untitled Course") == "Untitled Course"


def test_long_course_title() -> None:
    course = BBCourse(id="_1_1", title=LONG_TITLE + "I/II",
                      availability=BBAvailability(available="Yes"))
    job = mock.Mock()
    job.session.fetch_contents.return_value = []

    title = Course(course, job).title
    assert len(title.encode()) <= MAX_NAME_BYTES
    assert "/" not in title


def test_long_external_link_is_written(tmp_path: Path) -> None:
    content = mock.Mock()
    content.contentHandler.url = "https://example.com"
    link = ExternalLink(content, None, mock.Mock())

    folder = tmp_path / safe_filename(LONG_TITLE)
    folder.mkdir()
    link.write(folder, run_now())

    written = list(folder.iterdir())
    assert len(written) == 1
    assert written[0].suffix in (".url", ".desktop")


def test_long_attachment_keeps_extension(tmp_path: Path) -> None:
    attachment = BBAttachment(id="_1_1", fileName=LONG_TITLE + ".pdf",
                              mimeType="application/pdf")
    job = mock.Mock()
    job.session.download.return_value = stream()

    Attachment(attachment, {}, job).write(tmp_path, run_now())

    [written] = tmp_path.iterdir()
    assert written.suffix == ".pdf"
    assert written.read_bytes() == b"data"


def test_attachment_name_with_separator(tmp_path: Path) -> None:
    attachment = BBAttachment(id="_1_1", fileName="notes 1/2.pdf",
                              mimeType="application/pdf")
    job = mock.Mock()
    job.session.download.return_value = stream()

    Attachment(attachment, {}, job).write(tmp_path, run_now())

    assert [p.name for p in tmp_path.iterdir()] == ["notes 1_2.pdf"]


def test_long_webdav_file_is_written(tmp_path: Path) -> None:
    webdav = WebDavFile.__new__(WebDavFile)
    webdav.title = LONG_TITLE
    webdav.extension = ".docx"
    webdav.valid = True
    webdav.stream = stream()

    webdav.write(tmp_path, run_now())

    [written] = tmp_path.iterdir()
    assert written.suffix == ".docx"
