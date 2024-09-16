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
from functools import partial

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from .assets import logo


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
        tr = partial(QCoreApplication.translate, self.__class__.__name__)
        self.setText(tr(
            "Should BlackboardSync redownload all files?"
        ))
        self.setInformativeText(tr(
            "Answer no if you intend to move all past downloads manually"
            " (Recommended)."
        ))
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)
        self.setIcon(QMessageBox.Icon.Question)
        self.setWindowIcon(logo())

    def yes(self) -> bool:
        return self.exec() == QMessageBox.StandardButton.Yes


class UpdateFoundDialog(QMessageBox):
    """Inform user about a new available update."""

    def __init__(self) -> None:
        super().__init__()
        tr = partial(QCoreApplication.translate, self.__class__.__name__)
        self.setText(tr(
            "A new version of BlackboardSync is now available!"
        ))
        self.setInformativeText(tr(
            "Please download the latest version from your preferred store."
        ))

        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowIcon(logo())


class UniNotSupportedDialog(QMessageBox):
    """Inform user that their university is not supported."""

    def __init__(self, url: str) -> None:
        super().__init__()
        tr = partial(QCoreApplication.translate, self.__class__.__name__)
        self.setText(tr(
            "Unfortunately, your university is not yet supported"
        ))
        self.setInformativeText(tr(
            "You can help us provide support for it by visiting our website, "
            "which you can access by pressing the help button."
        ))
        self.setStandardButtons(
            QMessageBox.StandardButton.Help | QMessageBox.StandardButton.Ok
        )
        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowIcon(logo())
        self._url = url

    def exec(self) -> int:
        result = super().exec()
        if result == QMessageBox.StandardButton.Help:
            webbrowser.open(self._url)
        return result


class LoginErrorDialog(QMessageBox):
    def __init__(self, url: str) -> None:
        super().__init__()
        tr = partial(QCoreApplication.translate, self.__class__.__name__)
        self.setText(tr(
            "There was an issue logging you in"
        ))
        self.setInformativeText(tr(
            "Please try again later, and if the error persists"
            " contact our support by pressing the button below."
        ))
        self.setStandardButtons(
            QMessageBox.StandardButton.Help | QMessageBox.StandardButton.Ok
        )
        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowIcon(logo())
        self._url = url

    def exec(self) -> int:
        result = super().exec()
        if result == QMessageBox.StandardButton.Help:
            webbrowser.open(self._url)
        return result
