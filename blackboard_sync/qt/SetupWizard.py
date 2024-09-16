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
# from typing import override
from datetime import datetime

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (QWizard, QWizardPage,
                             QCompleter, QComboBox,
                             QCheckBox, QSpinBox,
                             QLabel, QPushButton)

from .assets import load_ui, get_wizard_pixmap
from .dialogs import DirDialog, Dialogs


class SetupWizard(QWizard):
    """Guide user through initial setup process."""

    class Pages(IntEnum):
        INTRO = 0
        INSTITUTION = 1
        DOWNLOAD_LOCATION = 2
        DOWNLOAD_SINCE = 3
        LAST = 3

    def __init__(self, support_url: str, institutions: list[str],
                 selected: int | None = None):
        super().__init__()

        # Typing information
        self.uni_selection_page: QWizardPage
        self.sync_location_page: QWizardPage
        self.uni_selection_box: QComboBox
        self.since_all_checkbox: QCheckBox
        self.date_spinbox: QSpinBox
        self.autodetect_label: QLabel
        self.sync_location_button: QPushButton

        self._institutions = institutions
        self._support_url = support_url
        self._has_chosen_location = False
        self._init_ui(selected)

    def _init_ui(self, selected: int | None) -> None:
        load_ui(self)

        pixmap_roles = [
            QWizard.WizardPixmap.BackgroundPixmap
        ]

        for role in pixmap_roles:
            self.setPixmap(role, get_wizard_pixmap(role))

        # Institution
        self.uni_selection_box.addItems(self._institutions)
        self.uni_selection_box.clearEditText()
        self.autodetect_label.setVisible(selected is not None)

        self.completer = QCompleter(self._institutions, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.uni_selection_box.setCompleter(self.completer)

        # Download location
        self.sync_location_button.clicked.connect(
            self._choose_location
        )

        # Minimum year
        year = datetime.today().year
        self.date_spinbox.setRange(2000, year)
        self.date_spinbox.setValue(year)
        self.date_spinbox.setEnabled(False)
        self.since_all_checkbox.stateChanged.connect(self._toggle_all_content)

        # Prepare wizard
        self.register_fields()

        # Select autodetected university
        # Must happen after the fields are registered
        if selected is not None:
            self.uni_selection_box.setCurrentIndex(selected)

        self.dialogs = Dialogs()

    def register_fields(self) -> None:
        # Make these actions obligatory
        self.uni_selection_page.registerField(
            "userInstitution*",
            self.uni_selection_box.lineEdit()
        )

        self.sync_location_page.registerField(
            "syncLocation*",
            self.sync_location_button,
            property="text",
            changedSignal=self.sync_location_button.clicked
        )

    def _update_download_location_button(self) -> None:
        dir = self.download_location.name or str(self.download_location)
        self.sync_location_button.setText(dir)

    # @override
    def initializePage(self, id: int) -> None:
        if id == self.Pages.DOWNLOAD_LOCATION:
            if self._has_chosen_location:
                self._update_download_location_button()

    # @override
    def validateCurrentPage(self) -> bool:
        valid = True

        # Do not progress if institution is not valid
        if self.currentId() == self.Pages.INSTITUTION:
            if not self._institution_is_valid():
                self.dialogs.uni_not_supported_dialog(self._support_url)
                valid = False

        return valid

    @pyqtSlot()
    def _choose_location(self) -> None:
        location = DirDialog().choose()

        if location is not None:
            self.download_location = location

    @pyqtSlot(int)
    def _toggle_all_content(self, state: int) -> None:
        unchecked = Qt.CheckState(state) != Qt.CheckState.Checked
        self.date_spinbox.setEnabled(unchecked)

    def _institution_is_valid(self) -> bool:
        return self.institution == str(self.field("userInstitution"))

    @property
    def institution(self) -> str:
        """Name of selected institution."""
        return self.uni_selection_box.itemText(self.institution_index)

    @property
    def institution_index(self) -> int:
        """Index of selected institution."""
        return self.uni_selection_box.currentIndex()

    @property
    def download_location(self) -> Path:
        """Download location selected by user."""
        return self._download_location

    @download_location.setter
    def download_location(self, location: Path) -> None:
        self._download_location = location.resolve()
        self._update_download_location_button()
        self._has_chosen_location = True

    @property
    def min_year(self) -> int | None:
        """Minimum year selected by user."""
        if not self.since_all_checkbox.isChecked():
            return self.date_spinbox.value()
        return None
