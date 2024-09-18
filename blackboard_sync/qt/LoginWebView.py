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

import webbrowser
from threading import Timer
from requests.cookies import RequestsCookieJar

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject, QUrl
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWebEngineCore import QWebEngineCookieStore, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .assets import load_ui, get_theme_icon, AppIcon


WATCHDOG_DELAY = 30


class LoginWebView(QWidget):
    """Login to a Blackboard instance using a browser."""

    class Signals(QObject):
        login_complete = pyqtSignal()

    def __init__(self, help_url: str) -> None:
        super().__init__()

        # Typing information
        self.web_view: QWebEngineView
        self.home_button: QPushButton
        self.back_button: QPushButton
        self.help_button: QPushButton
        self.status: QLabel

        self.watchdog: Timer | None

        self.start_url: str | None = None
        self.target_url: str | None = None

        self._cookie_jar = RequestsCookieJar()
        self.help_url = help_url

        self.signals = self.Signals()

        self._init_ui()

    def _init_ui(self) -> None:
        load_ui(self)

        self.home_button.setIcon(get_theme_icon(AppIcon.HOME))
        self.back_button.setIcon(get_theme_icon(AppIcon.BACK))
        self.help_button.setIcon(get_theme_icon(AppIcon.HELP))
        self.help_button.setVisible(False)

        self.init_signals()

    def init_signals(self) -> None:
        profile, cookie_store = self.get_profile_and_cookie_store()
        self.web_view.loadFinished.connect(self.slot_load_finished)
        self.home_button.clicked.connect(self.home)
        self.back_button.clicked.connect(self.web_view.back)
        self.help_button.clicked.connect(self.slot_help)

        if profile is not None:
            profile.clearHttpCacheCompleted.connect(self.slot_cache_cleared)
        if cookie_store is not None:
            cookie_store.cookieAdded.connect(self.slot_cookie_added)

    def load(self, start_url: str | None, target_url: str | None) -> None:
        self.start_url = start_url
        self.target_url = target_url

        # start watchdog
        self.watchdog = Timer(WATCHDOG_DELAY, self.show_help)
        self.watchdog.start()

        self.home()

    def home(self) -> None:
        self.web_view.load(QUrl.fromUserInput(self.start_url))

    @pyqtSlot()
    def slot_load_finished(self) -> None:
        """Check if we have reached the target url."""
        if self.target_url and self.url.startswith(self.target_url):
            if self.watchdog:
                self.watchdog.cancel()
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

    @pyqtSlot()
    def slot_cache_cleared(self) -> None:
        self.home()

    @pyqtSlot()
    def slot_help(self) -> None:
        webbrowser.open(self.help_url)

    def show_help(self) -> None:
        self.status.setText(self.tr(
            "Trouble logging in? Press the help button to let us know."
        ))
        self.help_button.setVisible(True)

    def restore(self) -> None:
        """Restore web view to original state."""
        self.clear_browser()

    def clear_browser(self) -> None:
        profile, cookie_store = self.get_profile_and_cookie_store()

        if cookie_store is not None:
            cookie_store.deleteAllCookies()
        if profile is not None:
            profile.clearHttpCache()

        self._cookie_jar = RequestsCookieJar()

    def get_profile_and_cookie_store(
        self
    ) -> tuple[QWebEngineProfile | None, QWebEngineCookieStore | None]:
        page = self.web_view.page()
        profile = None
        cookie_store = None

        if page is not None:
            profile = page.profile()

        if profile is not None:
            cookie_store = profile.cookieStore()

        return (profile, cookie_store)

    def cancel_watchdog(self) -> None:
        if self.watchdog:
            self.watchdog.cancel()

    @property
    def url(self) -> str:
        """URL of current website."""
        return self.web_view.url().toString()

    @property
    def cookies(self) -> RequestsCookieJar:
        """Contains session cookies of the current session."""
        return self._cookie_jar
