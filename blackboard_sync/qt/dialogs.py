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

from PyQt6.QtCore import QObject
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


class Dialogs(QObject):
    def __init__(self) -> None:
        super().__init__()

    def redownload_dialog(self) -> bool:
        q = QMessageBox()
        q.setText(self.tr("Do you wish to redownload all files?"))
        q.setInformativeText(self.tr(
            "Answer no if you intend to move all past downloads manually"
            " (Recommended)."
        ))
        q.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        q.setDefaultButton(QMessageBox.StandardButton.No)
        q.setIcon(QMessageBox.Icon.Question)
        q.setWindowIcon(logo())
        return q.exec() == QMessageBox.StandardButton.Yes

    def uni_not_supported_dialog(self, url: str) -> None:
        q = QMessageBox()
        q.setText(self.tr(
            "Unfortunately, your university is not yet supported"
        ))
        q.setInformativeText(self.tr(
            "You can help us provide support for it by visiting our website, "
            "which you can access by pressing the help button."
        ))
        q.setStandardButtons(
            QMessageBox.StandardButton.Help | QMessageBox.StandardButton.Ok
        )
        q.setIcon(QMessageBox.Icon.Warning)
        q.setWindowIcon(logo())

        if q.exec() == QMessageBox.StandardButton.Help:
            webbrowser.open(url)

    def login_error_dialog(self, url: str) -> None:
        q = QMessageBox()
        q.setText(self.tr(
            "There was an issue logging you in"
        ))
        q.setInformativeText(self.tr(
            "Please try again later, and if the error persists"
            " contact our support by pressing the button below."
        ))
        q.setStandardButtons(
            QMessageBox.StandardButton.Help | QMessageBox.StandardButton.Ok
        )
        q.setIcon(QMessageBox.Icon.Warning)
        q.setWindowIcon(logo())

        if q.exec() == QMessageBox.StandardButton.Help:
            webbrowser.open(url)
