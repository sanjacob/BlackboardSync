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

from enum import IntEnum
from pathlib import Path

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtWidgets import QComboBox, QPushButton, QDialogButtonBox

from .assets import load_ui
from .dialogs import DirDialog


class SettingsWindow(QWidget):
    """Tweaks main application preferences."""

    class SyncPeriod(IntEnum):
        HALF_HOUR = 60 * 30
        ONE_HOUR = 60 * 60
        SIX_HOURS = 60 * 60 * 6

    class Signals(QObject):
        log_out = pyqtSignal()
        setup_wiz = pyqtSignal()
        save = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # Typing information
        self.frequency_combo: QComboBox
        self.current_session_label: QLabel
        self.download_location_hint: QLabel
        self.version_label: QLabel
        self.select_download_location: QPushButton
        self.log_out_button: QPushButton
        self.setup_button: QPushButton
        self.button_box: QDialogButtonBox

        self.signals = self.Signals()

        self._init_ui()

    def _init_ui(self) -> None:
        load_ui(self)

        # Slots
        self.select_download_location.clicked.connect(self._choose_location)

        # Signals
        self.log_out_button.clicked.connect(self.signals.log_out)
        self.setup_button.clicked.connect(self.signals.setup_wiz)
        self.button_box.accepted.connect(self.signals.save)

    @pyqtSlot()
    def _choose_location(self) -> None:
        location = DirDialog().choose()

        if location is not None:
            self.download_location = location

    @property
    def download_location(self) -> Path:
        """Current download location."""
        return self._download_location

    @download_location.setter
    def download_location(self, location: Path) -> None:
        self._download_location = location.resolve()
        self.download_location_hint.setText(str(self._download_location))

    @property
    def sync_frequency(self) -> int:
        """Seconds to wait between each sync job."""
        options = list(self.SyncPeriod)
        return int(options[self.frequency_combo.currentIndex()])

    @sync_frequency.setter
    def sync_frequency(self, s: int) -> None:
        options = list(self.SyncPeriod)
        current = options.index(self.SyncPeriod(s))
        self.frequency_combo.setCurrentIndex(current)

    @property
    def username(self) -> str:
        """Username of current session."""
        return self.current_session_label.text()

    @username.setter
    def username(self, username: str) -> None:
        if username:
            self.current_session_label.setText(
                self.tr("Logged in as ") + username)
        else:
            self.current_session_label.setText(
                self.tr("Not currently logged in"))

    @property
    def version(self) -> str | None:
        return self.version_label.text()

    @version.setter
    def version(self, value: str | None) -> None:
        if value is None:
            value = self.tr("No version detected")
        self.version_label.setText(value)
