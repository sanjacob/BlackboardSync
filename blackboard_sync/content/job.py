from datetime import datetime, timezone

from blackboard.api_extended import BlackboardExtended


UNIX_EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)


class DownloadJob:
    def __init__(self, session: BlackboardExtended,
                 last_downloaded: datetime | None):
        self._last_downloaded = last_downloaded or UNIX_EPOCH
        self._session = session
        self._cancelled = False

    def has_changed(self, modified: datetime | None) -> bool:
        if modified is not None:
            return (modified >= self._last_downloaded)
        return True

    @property
    def session(self) -> BlackboardExtended:
        return self._session

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True
