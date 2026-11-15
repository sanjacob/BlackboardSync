from pathlib import Path
from unittest import mock
from datetime import datetime, timezone

import pytest
from hypothesis import given, strategies as st

from blackboard.blackboard import BBAttachment

from blackboard_sync.content import base
from blackboard_sync.content.base import BStream, FStream
from blackboard_sync.content.attachment import Attachment
from blackboard_sync.content.naming import split_extension


def run_now() -> mock.Mock:
    return mock.Mock(submit=lambda fn: fn())


def attachment_name(file_name: str | None, mime: str | None) -> str:
    attachment = BBAttachment(id="_1_1", fileName=file_name, mimeType=mime)
    return Attachment(attachment, {}, mock.Mock()).filename


# Extensions (#515)

@pytest.mark.parametrize("name, mime", [
    ("Lab1.ipynb", "application/octet-stream"),
    ("solve.m", "text/x-matlab"),
    ("solve.m", "application/octet-stream"),
    ("invoice.docm", "application/vnd.ms-word.document.macroEnabled.12"),
    ("notes.pdf", "application/pdf"),
    ("notes.pdf", "text/plain"),          # a wrong MIME type changes nothing
    ("archive.tar.gz", "application/gzip"),
    ("model.STL", None),
])
def test_uploaded_extension_is_kept(name: str, mime: str | None) -> None:
    assert attachment_name(name, mime) == name


@pytest.mark.parametrize("name, mime, expected", [
    ("Syllabus", "application/pdf", "Syllabus.pdf"),
    ("Chapter 3.1", "application/pdf", "Chapter 3.1.pdf"),
    ("v2. final", "text/plain", "v2. final.txt"),
    ("README", None, "README.txt"),
    ("blob", "application/x-unknown-type", "blob.txt"),
])
def test_extension_guessed_only_when_missing(name: str, mime: str | None,
                                             expected: str) -> None:
    assert attachment_name(name, mime) == expected


def test_unnamed_attachment_gets_a_name_and_extension() -> None:
    name = attachment_name(None, "application/pdf")
    assert name.endswith(".pdf") and len(name) > len(".pdf")


@pytest.mark.parametrize("name, expected", [
    ("notes.pdf", ("notes", ".pdf")),
    ("archive.tar.gz", ("archive.tar", ".gz")),
    ("Chapter 3.1", ("Chapter 3.1", "")),
    ("v2. final", ("v2. final", "")),
    ("README", ("README", "")),
    (".gitignore", (".gitignore", "")),
    ("trailing.", ("trailing.", "")),
    ("x.verylongextension", ("x.verylongextension", "")),
])
def test_split_extension(name: str, expected: tuple[str, str]) -> None:
    assert split_extension(name) == expected


@given(st.text())
def test_split_extension_round_trips(name: str) -> None:
    stem, ext = split_extension(name)
    assert stem + ext == name
    assert ext == "" or (ext[0] == "." and ext[1:].isalnum())


# Marked as downloaded from the internet

FILE_TIME = datetime(2024, 11, 3, 14, 45, tzinfo=timezone.utc)


def zone(path: Path) -> Path:
    # On Linux ':' is a normal character, so the Windows alternate data
    # stream shows up as a sibling file we can inspect
    return Path(f"{path}:Zone.Identifier")


@pytest.fixture
def windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(base.sys, "platform", "win32")


def stream(data: bytes = b"data") -> mock.Mock:
    return mock.Mock(iter_content=lambda chunk_size: [data])


def test_downloaded_file_is_marked_on_windows(tmp_path: Path,
                                              windows: None) -> None:
    path = tmp_path / "notes.pdf"
    BStream().save_stream(path, stream(), FILE_TIME)

    assert path.read_bytes() == b"data"
    assert zone(path).read_text() == "[ZoneTransfer]\nZoneId=3\n"
    assert path.stat().st_mtime == FILE_TIME.timestamp()


def test_written_file_is_marked_on_windows(tmp_path: Path,
                                           windows: None) -> None:
    path = tmp_path / "page.html"
    FStream().write_base(path, run_now(), "<p>hi</p>", FILE_TIME)

    assert zone(path).read_text() == "[ZoneTransfer]\nZoneId=3\n"
    assert path.stat().st_mtime == FILE_TIME.timestamp()


def test_attachment_is_marked_on_windows(tmp_path: Path,
                                         windows: None) -> None:
    job = mock.Mock()
    job.session.download.return_value = stream()
    pdf = BBAttachment(id="_1_1", fileName="notes.pdf",
                       mimeType="application/pdf")

    Attachment(pdf, {}, job).write(tmp_path, run_now())

    assert zone(tmp_path / "notes.pdf").exists()


def test_marking_failure_is_ignored(tmp_path: Path, windows: None) -> None:
    path = tmp_path / "notes.pdf"
    zone(path).mkdir()  # makes opening the stream fail, like FAT32 would

    BStream().save_stream(path, stream(), FILE_TIME)

    assert path.read_bytes() == b"data"
    assert path.stat().st_mtime == FILE_TIME.timestamp()


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_not_marked_elsewhere(tmp_path: Path,
                              monkeypatch: pytest.MonkeyPatch,
                              platform: str) -> None:
    monkeypatch.setattr(base.sys, "platform", platform)
    path = tmp_path / "notes.pdf"

    BStream().save_stream(path, stream())
    FStream().write_base(tmp_path / "page.html", run_now(), "x")

    assert sorted(p.name for p in tmp_path.iterdir()) == \
        ["notes.pdf", "page.html"]


def test_macos_app_quarantines_its_files() -> None:
    spec = (Path(__file__).parent.parent / "BlackboardSync.spec").read_text()
    assert "'LSFileQuarantineEnabled': True" in spec
