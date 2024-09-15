# Copyright (C) 2024, Jacob Sánchez Pérez

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

from requests.cookies import RequestsCookieJar

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject, QUrl
from PyQt6.QtWidgets import QWidget
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWebEngineCore import QWebEngineCookieStore, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .assets import load_ui


class LoginWebView(QWidget):
    """Login to a Blackboard instance using a browser."""

    class Signals(QObject):
        login_complete = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # Typing information
        self.web_view: QWebEngineView

        self.start_url: str | None = None
        self.target_url: str | None = None

        self._cookie_jar = RequestsCookieJar()

        self.signals = self.Signals()

        self._init_ui()

    def _init_ui(self) -> None:
        load_ui(self)
        self.web_view.loadFinished.connect(self.slot_load_finished)

    def load(self, start_url: str | None, target_url: str | None) -> None:
        self.start_url = start_url
        self.target_url = target_url

        self.web_view.load(QUrl.fromUserInput(self.start_url))

        if self._cookie_store is not None:
            self._cookie_store.cookieAdded.connect(self.slot_cookie_added)

    @pyqtSlot()
    def slot_load_finished(self) -> None:
        """Check if we have reached the target url."""
        if self.target_url and self.url.startswith(self.target_url):
            self.signals.login_complete.emit()

    @pyqtSlot(QNetworkCookie)
    def slot_cookie_added(self, cookie: QNetworkCookie) -> None:
        """Add the cookie to our own jar."""
        self._cookie_jar.set(
            cookie.name().data().decode(),
            cookie.value().data().decode(),
            domain=cookie.domain(),
            path=cookie.path(),
            secure=cookie.isSecure()
        )

    def restore(self) -> None:
        """Restore web view to original state."""
        self.web_view.setPage(None)
        self.clear_browser()
        self.load(self.start_url, self.target_url)

    def clear_browser(self) -> None:
        if self._engine_profile is not None:
            self._engine_profile.clearHttpCache()
        if self._cookie_store is not None:
            self._cookie_store.deleteAllCookies()

    @property
    def _engine_profile(self) -> QWebEngineProfile | None:
        page = self.web_view.page()
        return page.profile() if page else None

    @property
    def _cookie_store(self) -> QWebEngineCookieStore | None:
        profile = self._engine_profile
        return profile.cookieStore() if profile else None

    @property
    def url(self) -> str:
        """URL of current website."""
        return self.web_view.url().toString()

    @property
    def cookies(self) -> RequestsCookieJar:
        """Contains session cookies of the current session."""
        return self._cookie_jar
