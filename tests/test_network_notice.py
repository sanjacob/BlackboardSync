from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
from requests.exceptions import (
    ChunkedEncodingError,
    ConnectionError,
    ReadTimeout,
    SSLError,
)

from blackboard_sync import sync
from blackboard_sync.executor import SyncExecutor
from blackboard_sync.content.base import BStream
from blackboard_sync.sync_controller import SyncController
from blackboard_sync.qt.notification import Event, TrayMessages

from tests.test_resume import DATA, Server


@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BStream, "RETRY_DELAY", 0)


def download_with(executor: SyncExecutor, server: Server, path: Path) -> None:
    BStream().write_base(executor, server,
                         lambda s: BStream().save_stream(path, s), "file")
    executor.shutdown()
    executor.raise_exceptions()


# Detection in the download workers

def test_clean_download_is_not_reported(tmp_path: Path) -> None:
    executor = SyncExecutor()
    download_with(executor, Server(DATA, [None]), tmp_path / "f")
    assert not executor.network_unstable


def test_single_recovered_interruption_is_reported(tmp_path: Path) -> None:
    executor = SyncExecutor()
    download_with(executor, Server(DATA, [3000, None]), tmp_path / "f")

    assert (tmp_path / "f").read_bytes() == DATA
    assert executor.network_unstable


def test_failed_download_is_reported(tmp_path: Path) -> None:
    executor = SyncExecutor()

    with pytest.raises(ChunkedEncodingError):
        download_with(executor, Server(DATA, [3000] + [0] * 50),
                      tmp_path / "f")

    assert executor.network_unstable


def test_other_executors_still_work(tmp_path: Path) -> None:
    path = tmp_path / "f"
    BStream().write_base(mock.Mock(submit=lambda fn: fn()),
                         Server(DATA, [3000, None]),
                         lambda s: BStream().save_stream(path, s), "file")
    assert path.read_bytes() == DATA


# The sync model's flag

class FakeDownload:
    def __init__(self, error: Exception | None = None,
                 unstable: bool = False) -> None:
        self.error, self.network_unstable = error, unstable

    def __call__(self, *args: object) -> "FakeDownload":
        return self

    def download(self) -> None:
        if self.error:
            raise self.error


@pytest.fixture
def model(tmp_path: Path,
          monkeypatch: pytest.MonkeyPatch) -> sync.BlackboardSync:
    config = SimpleNamespace(university_index=None, last_sync_time=None,
                             download_location=tmp_path, min_year=None)
    monkeypatch.setattr(sync, "SyncConfig", lambda: config)
    monkeypatch.setattr(sync.BlackboardSync, "_add_logger_file_handler",
                        lambda self: None)

    model = sync.BlackboardSync()
    model.sess = mock.Mock()
    model.university = mock.Mock()
    model._is_active = True
    return model


def run(model: sync.BlackboardSync, monkeypatch: pytest.MonkeyPatch,
        fake: FakeDownload) -> None:
    monkeypatch.setattr(sync, "BlackboardDownload", fake)
    model.download()


@pytest.mark.parametrize("error", [
    ConnectionError("reset"), ReadTimeout("slow"), SSLError("EOF"),
    ChunkedEncodingError("IncompleteRead"),
])
def test_sync_failing_on_network_error_flags_unstable(
        model: sync.BlackboardSync, monkeypatch: pytest.MonkeyPatch,
        error: Exception) -> None:
    run(model, monkeypatch, FakeDownload(error))

    assert model.unstable_network
    assert not model.unstable_network  # read once, like has_error
    assert model.has_error


def test_sync_failing_otherwise_is_not_unstable(
        model: sync.BlackboardSync, monkeypatch: pytest.MonkeyPatch) -> None:
    run(model, monkeypatch, FakeDownload(ValueError("bug")))

    assert not model.unstable_network
    assert model.has_error


def test_recovered_interruption_flags_unstable_without_error(
        model: sync.BlackboardSync, monkeypatch: pytest.MonkeyPatch) -> None:
    run(model, monkeypatch, FakeDownload(unstable=True))

    assert model.unstable_network
    assert not model.has_error


def test_clean_sync_is_not_unstable(
        model: sync.BlackboardSync, monkeypatch: pytest.MonkeyPatch) -> None:
    run(model, monkeypatch, FakeDownload())

    assert not model.unstable_network
    assert not model.has_error


# The notification on opening the menu

@pytest.mark.parametrize("has_error, unstable, shown", [
    (False, False, None),
    (True, False, "notify_sync_error"),
    (False, True, "notify_unstable_network"),
    (True, True, "notify_unstable_network"),
])
def test_menu_notification(has_error: bool, unstable: bool,
                           shown: str | None) -> None:
    controller = SyncController.__new__(SyncController)
    controller.model = mock.Mock(has_error=has_error,
                                 unstable_network=unstable)
    controller.ui = mock.Mock()

    controller.open_menu()

    for name in ("notify_sync_error", "notify_unstable_network"):
        assert getattr(controller.ui, name).called == (name == shown)


def test_unstable_network_message(qtbot) -> None:
    title, msg, severity, _ = TrayMessages().get_msg(Event.UNSTABLE_NETWORK)
    assert "unstable" in title
    assert "resumed automatically" in msg
