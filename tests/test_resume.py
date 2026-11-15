import random
import hashlib
import threading
from pathlib import Path
from unittest import mock
from collections.abc import Callable, Iterator

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from requests import Response
from requests.exceptions import ChunkedEncodingError, ConnectionError
from requests.structures import CaseInsensitiveDict
from urllib3.exceptions import ProtocolError, ReadTimeoutError, SSLError

from blackboard.blackboard import BBAttachment

from blackboard_sync.executor import SyncExecutor
from blackboard_sync.content import base
from blackboard_sync.content.attachment import Attachment
from blackboard_sync.content.base import BStream, ResumeError
from blackboard_sync.content.webdav import Link, WebDavFile


DATA = bytes(range(256)) * 40  # 10 KiB
MAX = BStream.MAX_RETRIES


@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BStream, "RETRY_DELAY", 0)


def broken_pipe() -> Exception:
    return ProtocolError("Connection broken: IncompleteRead")


class BrokenRaw:
    """A urllib3-like body that raises `error()` after `cut` bytes."""

    def __init__(self, data: bytes | memoryview, cut: int | None,
                 error: Callable[[], Exception]) -> None:
        self.data, self.cut, self.error = data, cut, error

    def stream(self, chunk_size: int, decode_content: bool) -> Iterator[bytes]:
        end = len(self.data) if self.cut is None else self.cut

        for i in range(0, end, chunk_size):
            yield bytes(self.data[i:min(i + chunk_size, end)])

        if self.cut is not None:
            raise self.error()

    def close(self) -> None:
        pass


class TrackedResponse(Response):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False

    def close(self) -> None:
        self.closed = True
        super().close()


def response(status: int, body: bytes | memoryview, cut: int | None = None,
             error: Callable[[], Exception] = broken_pipe,
             **headers: str) -> TrackedResponse:
    r = TrackedResponse()
    r.status_code = status
    r.headers = CaseInsensitiveDict(headers)
    r.raw = BrokenRaw(body, cut, error)
    return r


class Server:
    """Serves `data`; response i breaks after `cuts[i]` bytes of its body.

    A cut of None, or one at least as long as the body, sends the body
    complete. Once the cuts run out, responses are complete.
    """

    def __init__(self, data: bytes, cuts: list[int | None],
                 ignore_range: bool = False, gzip: bool = False,
                 length: bool = True,
                 error: Callable[[], Exception] = broken_pipe) -> None:
        self.data = memoryview(data)
        self.cuts = list(cuts)
        self.ignore_range = ignore_range
        self.error = error
        self.headers = {"Content-Encoding": "gzip"} if gzip else {}
        self.length = length
        self.requests: list[dict[str, str]] = []
        self.responses: list[TrackedResponse] = []

    def __call__(self, headers: dict[str, str] | None = None,
                 **_: str) -> Response:
        headers = dict(headers or {})
        self.requests.append(headers)
        cut = self.cuts.pop(0) if self.cuts else None
        size = len(self.data)
        extra = dict(self.headers)

        if "Range" in headers and not self.ignore_range:
            start = int(headers["Range"].removeprefix("bytes=").rstrip("-"))
            body = self.data[start:]
            status = 206
            extra["Content-Range"] = f"bytes {start}-{size - 1}/{size}"
        else:
            body, status = self.data, 200

        if self.length:
            extra["Content-Length"] = str(len(body))
        if cut is not None and cut >= len(body):
            cut = None

        r = response(status, body, cut, self.error, **extra)
        self.responses.append(r)
        return r


def run_now() -> mock.Mock:
    return mock.Mock(submit=lambda fn: fn())


def save(download: Callable[..., Response], path: Path) -> Path:
    BStream().write_base(run_now(), download,
                         lambda s: BStream().save_stream(path, s), "file")
    return path


# Property test

def expected(size: int, cuts: list[int | None],
             ignore_range: bool) -> tuple[bool, list[int]]:
    """Model: (succeeds?, offsets of every request made)."""
    received, failures, offsets = 0, 0, []

    for cut in cuts + [None]:
        offsets.append(received)
        body = size if ignore_range else size - received

        if cut is None or cut >= body:
            return True, offsets

        new = max(0, cut - received) if ignore_range else cut
        received += new
        failures = 1 if new else failures + 1

        if failures > MAX:
            return False, offsets

    raise AssertionError("unreachable")


@settings(max_examples=300, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=st.binary(max_size=6000),
       cuts=st.lists(st.one_of(st.none(), st.integers(0, 7000),
                               st.just(0)), max_size=25),
       ignore_range=st.booleans(), gzip=st.booleans(),
       length=st.booleans(), etag=st.booleans())
def test_resume_property(tmp_path: Path, data: bytes, cuts: list[int | None],
                         ignore_range: bool, gzip: bool,
                         length: bool, etag: bool) -> None:
    # Content-Encoding makes the client restart without Range, which the
    # model treats exactly like a server that ignores Range
    no_range = ignore_range or gzip
    succeeds, offsets = expected(len(data), cuts, no_range)
    server = Server(data, cuts, ignore_range, gzip, length)
    if etag:
        server.headers["ETag"] = '"v1"'
    path = tmp_path / "file.bin"
    path.unlink(missing_ok=True)

    if succeeds:
        assert save(server, path).read_bytes() == data
    else:
        with pytest.raises(ChunkedEncodingError):
            save(server, path)

    assert len(server.requests) == len(offsets)

    # Range is used unless compressed, until a server ignores it once
    ranges = not gzip

    for headers, offset in zip(server.requests, offsets):
        if not ranges or offset == 0:
            assert headers == {}
        else:
            expected_headers = {"Range": f"bytes={offset}-"}
            if etag:
                expected_headers["If-Range"] = '"v1"'
            assert headers == expected_headers
            ranges = not ignore_range

    assert all(r.closed for r in server.responses)


# Targeted cases

def test_complete_download_needs_one_request(tmp_path: Path) -> None:
    server = Server(DATA, [None])
    assert save(server, tmp_path / "f").read_bytes() == DATA
    assert server.requests == [{}]


def test_empty_file(tmp_path: Path) -> None:
    server = Server(b"", [None])
    assert save(server, tmp_path / "f").read_bytes() == b""
    assert len(server.requests) == 1


def test_resumes_from_last_byte(tmp_path: Path) -> None:
    server = Server(DATA, [3000, None])
    assert save(server, tmp_path / "f").read_bytes() == DATA
    assert server.requests == [{}, {"Range": "bytes=3000-"}]


def test_never_gives_up_while_progressing(tmp_path: Path) -> None:
    cuts: list[int | None] = [100] * (MAX * 10)
    server = Server(DATA, cuts)
    assert save(server, tmp_path / "f").read_bytes() == DATA
    assert len(server.requests) == MAX * 10 + 1


def test_gives_up_after_max_retries_without_progress(tmp_path: Path) -> None:
    server = Server(DATA, [3000] + [0] * 50)

    with pytest.raises(ChunkedEncodingError):
        save(server, tmp_path / "f")

    assert len(server.requests) == 1 + MAX
    assert all(r.closed for r in server.responses)


def test_progress_resets_the_retry_count(tmp_path: Path) -> None:
    # MAX - 1 stalls, a little progress, MAX - 1 stalls again: succeeds
    stalls = [0] * (MAX - 1)
    server = Server(DATA, [1000] + stalls + [10] + stalls + [None])
    assert save(server, tmp_path / "f").read_bytes() == DATA


@pytest.mark.parametrize("error", [
    broken_pipe,
    lambda: ReadTimeoutError(None, "/file", "Read timed out."),  # type: ignore
    lambda: SSLError("EOF occurred in violation of protocol"),
])
def test_each_kind_of_interruption(tmp_path: Path,
                                   error: Callable[[], Exception]) -> None:
    server = Server(DATA, [2500, 5000, None], error=error)
    assert save(server, tmp_path / "f").read_bytes() == DATA
    assert server.requests[1:] == [{"Range": "bytes=2500-"},
                                   {"Range": "bytes=7500-"}]


def test_big_file_with_many_interruptions(tmp_path: Path) -> None:
    rng = random.Random(566)
    data = rng.randbytes(64 * 1024 * 1024)  # 64 MiB
    cuts: list[int | None] = [rng.randrange(1, 4 * 1024 * 1024)
                              for _ in range(30)]
    server = Server(data, cuts)

    path = save(server, tmp_path / "big.bin")

    assert path.stat().st_size == len(data)
    assert hashlib.sha256(path.read_bytes()).digest() == \
        hashlib.sha256(data).digest()
    assert len(server.requests) == 31


def test_big_file_server_ignoring_range(tmp_path: Path) -> None:
    rng = random.Random(685)
    data = rng.randbytes(8 * 1024 * 1024)  # 8 MiB, resent in full each time
    cuts: list[int | None] = [1024 * 1024 * i for i in range(1, 8)]
    server = Server(data, cuts, ignore_range=True)

    path = save(server, tmp_path / "big.bin")
    assert path.read_bytes() == data


def test_unknown_length_resumes(tmp_path: Path) -> None:
    server = Server(DATA, [4000, None], length=False)
    assert save(server, tmp_path / "f").read_bytes() == DATA
    assert server.requests == [{}, {"Range": "bytes=4000-"}]


def test_break_after_last_byte_is_complete(tmp_path: Path) -> None:
    def ends_badly(headers: dict[str, str] | None = None) -> Response:
        return response(200, DATA, len(DATA),
                        **{"Content-Length": str(len(DATA))})

    assert save(ends_badly, tmp_path / "f").read_bytes() == DATA


def test_server_error_on_resume_is_retried(tmp_path: Path) -> None:
    server = Server(DATA, [3000, None])
    errors = iter([503, 502])

    def flaky(headers: dict[str, str] | None = None) -> Response:
        if headers and (status := next(errors, None)):
            return response(status, b"busy")
        return server(headers)

    assert save(flaky, tmp_path / "f").read_bytes() == DATA


def test_failed_reconnect_is_retried(tmp_path: Path) -> None:
    server = Server(DATA, [3000, None])
    errors = iter([ConnectionError("down"), ConnectionError("down")])

    def flaky(headers: dict[str, str] | None = None) -> Response:
        if headers and (error := next(errors, None)):
            raise error
        return server(headers)

    assert save(flaky, tmp_path / "f").read_bytes() == DATA
    assert server.requests == [{}, {"Range": "bytes=3000-"}]


def test_backoff_grows_between_stalled_attempts(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BStream, "RETRY_DELAY", 2.0)
    sleeps: list[float] = []
    monkeypatch.setattr(base.time, "sleep", sleeps.append)

    save(Server(DATA, [3000, 0, 0, None]), tmp_path / "f")

    assert sleeps == [2.0, 4.0, 6.0]


def range_server(on_range: Callable[[], Response]) -> Callable[..., Response]:
    """Breaks at 3000 at first; answers Range requests with `on_range()`
    and plain requests with the whole file."""
    def download(headers: dict[str, str] | None = None) -> Response:
        download.requests.append(dict(headers or {}))  # type: ignore
        first = len(download.requests) == 1  # type: ignore[attr-defined]
        if headers and "Range" in headers:
            return on_range()
        return response(200, DATA, 3000 if first else None,
                        **{"Content-Length": str(len(DATA))})

    download.requests = []  # type: ignore[attr-defined]
    return download


@pytest.mark.parametrize("on_range", [
    lambda: response(416, b""),
    lambda: response(501, b""),
    lambda: response(206, DATA[10:],  # resumed from the wrong position
                     **{"Content-Range": f"bytes 10-10239/{len(DATA)}"}),
    lambda: response(206, DATA[3000:], **{"Content-Range": "garbage"}),
], ids=["416", "501", "wrong start", "unparseable"])
def test_unsupported_ranges_fall_back_to_full_download(
        tmp_path: Path, on_range: Callable[[], Response]) -> None:
    download = range_server(on_range)
    assert save(download, tmp_path / "f").read_bytes() == DATA
    assert download.requests == [  # type: ignore[attr-defined]
        {}, {"Range": "bytes=3000-"}, {}]


def test_accept_ranges_none_never_sends_range(tmp_path: Path) -> None:
    def download(headers: dict[str, str] | None = None) -> Response:
        assert not headers
        download.calls += 1  # type: ignore[attr-defined]
        cut = 3000 if download.calls == 1 else None  # type: ignore
        return response(200, DATA, cut, **{"Accept-Ranges": "none",
                                           "Content-Length": str(len(DATA))})

    download.calls = 0  # type: ignore[attr-defined]
    assert save(download, tmp_path / "f").read_bytes() == DATA
    assert download.calls == 2  # type: ignore[attr-defined]


def test_fallback_sticks_for_later_interruptions(tmp_path: Path) -> None:
    server = Server(DATA, [3000, 1000, 2000, None], ignore_range=True)
    assert save(server, tmp_path / "f").read_bytes() == DATA
    # Range was tried once, answered with the whole file, never again
    assert server.requests == [{}, {"Range": "bytes=3000-"}, {}, {}]


def test_changed_total_in_content_range_is_an_error(tmp_path: Path) -> None:
    download = range_server(lambda: response(
        206, DATA[3000:], **{"Content-Range": "bytes 3000-10239/99999"}))

    with pytest.raises(ResumeError):
        save(download, tmp_path / "f")


def test_unknown_total_in_content_range_is_accepted(tmp_path: Path) -> None:
    def star(headers: dict[str, str] | None = None) -> Response:
        if headers:
            return response(206, DATA[3000:],
                            **{"Content-Range": "bytes 3000-10239/*"})
        return response(200, DATA, 3000,
                        **{"Content-Length": str(len(DATA))})

    assert save(star, tmp_path / "f").read_bytes() == DATA


def test_changed_file_resent_in_full_is_an_error(tmp_path: Path) -> None:
    def changed(headers: dict[str, str] | None = None) -> Response:
        if headers:
            return response(200, DATA + b"new",
                            **{"Content-Length": str(len(DATA) + 3)})
        return response(200, DATA, 3000,
                        **{"Content-Length": str(len(DATA))})

    with pytest.raises(ResumeError):
        save(changed, tmp_path / "f")


def test_resent_file_shorter_than_received_is_an_error(
        tmp_path: Path) -> None:
    # No lengths to compare; the resent body ends before the resume point
    def shorter(headers: dict[str, str] | None = None) -> Response:
        if headers:
            raise AssertionError("must not use Range for gzip")
        if shorter.calls:  # type: ignore[attr-defined]
            return response(200, DATA[:1000], **{"Content-Encoding": "gzip"})
        shorter.calls += 1  # type: ignore[attr-defined]
        return response(200, DATA, 3000, **{"Content-Encoding": "gzip"})

    shorter.calls = 0  # type: ignore[attr-defined]

    with pytest.raises(ResumeError):
        save(shorter, tmp_path / "f")


def test_save_error_is_not_retried(tmp_path: Path) -> None:
    server = Server(DATA, [None])

    with pytest.raises(OSError):
        save(server, tmp_path / "missing" / "f")

    assert len(server.requests) == 1
    assert all(r.closed for r in server.responses)


def test_attachment_resumes(tmp_path: Path) -> None:
    server = Server(DATA, [4096, 2048, None])
    job = mock.Mock()
    job.session.download.side_effect = server
    pdf = BBAttachment(id="_1_1", fileName="notes.pdf",
                       mimeType="application/pdf")

    Attachment(pdf, {"course_id": "_1_1"}, job).write(tmp_path, run_now())

    assert (tmp_path / "notes.pdf").read_bytes() == DATA
    assert server.requests == [{}, {"Range": "bytes=4096-"},
                               {"Range": "bytes=6144-"}]
    assert all(r.closed for r in server.responses)


def test_webdav_resumes_with_first_response_headers(tmp_path: Path) -> None:
    server = Server(DATA, [5000, None])
    server.headers.update({"Content-Type": "application/pdf",
                           "Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"})

    def download(headers: dict[str, str] | None = None, **_: str) -> Response:
        r = server(headers)
        if headers:  # a resumed response must not decide name or time
            r.headers["Content-Type"] = "text/plain"
            del r.headers["Last-Modified"]
        return r

    job = mock.Mock()
    job.session.instance_url = "https://example.com"
    job.session.download_webdav.side_effect = download
    link = Link(href="https://example.com/bbcswebdav/notes", text="notes")

    WebDavFile(link, job).write(tmp_path, run_now())

    written = tmp_path / "notes.pdf"
    assert written.read_bytes() == DATA
    assert written.stat().st_mtime == 1730645100
    assert server.requests[1] == {"Range": "bytes=5000-",
                                  "If-Range": "Sun, 03 Nov 2024 14:45:00 GMT"}


def test_concurrent_downloads_all_resume(tmp_path: Path) -> None:
    rng = random.Random(758)
    servers = {}
    lock = threading.Lock()

    def download(attachment_id: str,
                 headers: dict[str, str] | None = None, **_: str) -> Response:
        with lock:
            return servers[attachment_id](headers)

    job = mock.Mock()
    job.session.download.side_effect = download
    attachments = []

    for i in range(40):
        data = rng.randbytes(rng.randrange(0, 200_000))
        cuts: list[int | None] = [rng.randrange(1, 50_000)
                                  for _ in range(rng.randrange(0, 6))]
        servers[f"_{i}_1"] = Server(data, cuts)
        att = BBAttachment(id=f"_{i}_1", fileName=f"f{i}.pdf",
                           mimeType="application/pdf")
        attachments.append((Attachment(att, {}, job), data))

    executor = SyncExecutor(max_workers=6)
    for attachment, _ in attachments:
        attachment.write(tmp_path, executor)
    executor.shutdown()
    executor.raise_exceptions()

    for attachment, data in attachments:
        assert (tmp_path / attachment.filename).read_bytes() == data

    assert all(r.closed for s in servers.values() for r in s.responses)


# File versions (ETag / Last-Modified)

def versioned(first: dict[str, str], later: dict[str, str],
              status: int = 206) -> Callable[..., Response]:
    """First response breaks at 3000 with headers `first`; later ones
    succeed with headers `later` (206 from 3000, or 200 in full)."""
    def download(headers: dict[str, str] | None = None) -> Response:
        download.requests.append(dict(headers or {}))  # type: ignore
        if not headers:
            return response(200, DATA, 3000,
                            **{"Content-Length": str(len(DATA))}, **first)
        if status == 206:
            return response(206, DATA[3000:], **later, **{
                "Content-Range": f"bytes 3000-{len(DATA) - 1}/{len(DATA)}"})
        return response(200, DATA, **later,
                        **{"Content-Length": str(len(DATA))})

    download.requests = []  # type: ignore[attr-defined]
    return download


def test_if_range_uses_strong_etag(tmp_path: Path) -> None:
    tag = {"ETag": '"abc"', "Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"}
    download = versioned(tag, tag)
    assert save(download, tmp_path / "f").read_bytes() == DATA
    assert download.requests[1] == {  # type: ignore[attr-defined]
        "Range": "bytes=3000-", "If-Range": '"abc"'}


def test_if_range_falls_back_to_last_modified(tmp_path: Path) -> None:
    tag = {"ETag": 'W/"abc"', "Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"}
    download = versioned(tag, tag)
    assert save(download, tmp_path / "f").read_bytes() == DATA
    assert download.requests[1] == {  # type: ignore[attr-defined]
        "Range": "bytes=3000-",
        "If-Range": "Sun, 03 Nov 2024 14:45:00 GMT"}


def test_no_validator_no_if_range(tmp_path: Path) -> None:
    download = versioned({}, {})
    assert save(download, tmp_path / "f").read_bytes() == DATA
    assert download.requests[1] == {  # type: ignore[attr-defined]
        "Range": "bytes=3000-"}


@pytest.mark.parametrize("status", [206, 200])
@pytest.mark.parametrize("first, later", [
    ({"ETag": '"v1"'}, {"ETag": '"v2"'}),
    ({"Last-Modified": "Sun, 03 Nov 2024 14:45:00 GMT"},
     {"Last-Modified": "Mon, 04 Nov 2024 09:00:00 GMT"}),
])
def test_new_version_is_never_stitched(tmp_path: Path, status: int,
                                       first: dict[str, str],
                                       later: dict[str, str]) -> None:
    # Same size, different version: lengths alone cannot tell them apart
    with pytest.raises(ResumeError):
        save(versioned(first, later, status), tmp_path / "f")


def test_same_version_resent_in_full_is_skipped(tmp_path: Path) -> None:
    tag = {"ETag": '"v1"'}
    path = save(versioned(tag, tag, status=200), tmp_path / "f")
    assert path.read_bytes() == DATA
