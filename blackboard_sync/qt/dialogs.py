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
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QFileDialog

from .assets import load_ui


class DirDialog(QFileDialog):
    """Open the file dialog in directory mode."""
    def init(self) -> None:
        super().__init__()

    def choose(self) -> Path | None:
        self.setFileMode(QFileDialog.FileMode.Directory)
        if super().exec():
            return Path(self.directory().path())
        return None


class RedownloadDialog(QMessageBox):
    """Ask user if files should be redownloaded to new location."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self)

    @property
    def yes(self) -> bool:
        return self.exec() == QMessageBox.StandardButton.Yes


class UpdateFoundDialog(QMessageBox):
    """Inform user about a new available update."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self)

    @property
    def yes(self) -> bool:
        return self.exec() == QMessageBox.StandardButton.Open


class UniNotSupportedDialog(QMessageBox):
    """Inform user that their university is not supported."""

    def __init__(self, help_url: str) -> None:
        super().__init__()
        load_ui(self)
        self._help_url = help_url

    def exec(self) -> int:
        result = super().exec()
        if result == QMessageBox.StandardButton.Help:
            webbrowser.open(self._help_url)
        return result
