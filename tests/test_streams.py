import threading
from pathlib import Path
from unittest import mock
from datetime import datetime, timezone

import pytest

from blackboard.blackboard import BBAttachment
from blackboard.exceptions import BBForbiddenError

from blackboard_sync.executor import SyncExecutor
from blackboard_sync.content.attachment import Attachment
from blackboard_sync.content.webdav import Link, WebDavFile


BASE_URL = "https://example.com"
PDF = BBAttachment(id="_1_1", fileName="notes.pdf", mimeType="application/pdf")


def run_now() -> mock.Mock:
    return mock.Mock(submit=lambda fn: fn())


def response(status: int = 200, data: bytes = b"data",
             **headers: str) -> mock.Mock:
    return mock.Mock(status_code=status, headers=headers,
                     iter_content=lambda chunk_size: [data])


def webdav(job: mock.Mock, href: str = BASE_URL + "/bbcswebdav/notes") \
        -> WebDavFile:
    job.session.instance_url = BASE_URL
    return WebDavFile(Link(href=href, text="notes"), job)


def test_attachment_opens_connection_only_when_written(tmp_path: Path) -> None:
    job = mock.Mock()
    job.session.download.return_value = resp = response()

    attachment = Attachment(PDF, {"course_id": "_1_1"}, job)
    job.session.download.assert_not_called()

    attachment.write(tmp_path, run_now())

    job.session.download.assert_called_once_with(attachment_id="_1_1",
                                                 course_id="_1_1")
    assert (tmp_path / "notes.pdf").read_bytes() == b"data"
    resp.close.assert_called_once()


def test_attachment_closed_when_saving_fails(tmp_path: Path) -> None:
    job = mock.Mock()
    job.session.download.return_value = resp = response()
    attachment = Attachment(PDF, {}, job)

    with pytest.raises(OSError):
        attachment.write(tmp_path / "missing folder", run_now())

    resp.close.assert_called_once()


def test_forbidden_attachment_is_skipped(tmp_path: Path, caplog) -> None:
    job = mock.Mock()
    job.session.download.side_effect = BBForbiddenError("403")

    Attachment(PDF, {}, job).write(tmp_path, run_now())

    assert not any(tmp_path.iterdir())
    assert "Could not download notes.pdf" in caplog.text


def test_webdav_opens_connection_only_when_written(tmp_path: Path) -> None:
    job = mock.Mock()
    job.session.download_webdav.return_value = resp = response(
        **{"Content-Type": "application/pdf",
           "Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"})

    file = webdav(job)
    job.session.download_webdav.assert_not_called()

    file.write(tmp_path, run_now())

    written = tmp_path / "notes.pdf"
    assert written.read_bytes() == b"data"
    assert written.stat().st_mtime == datetime(
        2024, 11, 3, 14, 45, tzinfo=timezone.utc).timestamp()
    resp.close.assert_called_once()


@pytest.mark.parametrize("resp, href", [
    (response(status=404), BASE_URL + "/bbcswebdav/notes"),
    (response(**{"Content-Type": "video/mp4"}), BASE_URL + "/bbcswebdav/v"),
    (response(), "https://elsewhere.com/notes"),
])
def test_rejected_webdav_closed(tmp_path: Path, resp: mock.Mock,
                                href: str) -> None:
    job = mock.Mock()
    job.session.download_webdav.return_value = resp

    webdav(job, href).write(tmp_path, run_now())

    assert not any(tmp_path.iterdir())
    resp.close.assert_called_once()


def test_open_connections_bounded_by_workers(tmp_path: Path) -> None:
    """Many files never hold more connections than there are workers."""
    workers = 3
    lock = threading.Lock()
    open_now = peak = 0
    responses = []

    def download(**_: str) -> mock.Mock:
        nonlocal open_now, peak

        def close() -> None:
            nonlocal open_now
            with lock:
                open_now -= 1

        with lock:
            open_now += 1
            peak = max(peak, open_now)

        resp = response()
        resp.close.side_effect = close
        responses.append(resp)
        return resp

    job = mock.Mock()
    job.session.download.side_effect = download

    attachments = [
        Attachment(BBAttachment(id=f"_{i}_1", fileName=f"file{i}.pdf",
                                mimeType="application/pdf"), {}, job)
        for i in range(50)
    ]
    assert open_now == 0  # building the tree opened nothing

    executor = SyncExecutor(max_workers=workers)
    for attachment in attachments:
        attachment.write(tmp_path, executor)
    executor.shutdown()
    executor.raise_exceptions()

    assert len(list(tmp_path.iterdir())) == 50
    assert 1 <= peak <= workers
    assert open_now == 0
    assert all(r.close.call_count == 1 for r in responses)
