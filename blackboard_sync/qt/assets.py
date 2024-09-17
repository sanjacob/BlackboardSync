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

from enum import Enum
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWizard


ICON_FILENAME = 'logo.png'


def load_ui(qt_obj: QObject) -> None:
    """Load a UI file for a `QObject`."""
    filename = qt_obj.__class__.__name__ + ".ui"
    filepath = Path(__file__).parent / filename
    uic.loadUi(filepath.resolve(), qt_obj)  # type: ignore


def get_asset(icon: str) -> Path:
    """Get the `Path` of a media asset."""
    root_dir = Path(__file__).parent.parent
    return (root_dir / 'assets' / icon).resolve()


def get_translations() -> str:
    qt_dir = Path(__file__).parent
    return str((qt_dir / "translations").resolve())


def get_icon(file: str) -> QIcon:
    return QIcon(str(get_asset(file)))


def logo() -> QIcon:
    return get_icon(ICON_FILENAME)


class AppIcon(Enum):
    EXIT = QIcon.ThemeIcon.ApplicationExit
    OPEN = QIcon.ThemeIcon.FolderOpen
    SYNC = QIcon.ThemeIcon.ViewRefresh
    HELP = QIcon.ThemeIcon.HelpAbout
    HOME = QIcon.ThemeIcon.GoHome
    BACK = QIcon.ThemeIcon.EditUndo


def get_theme_icon(icon: AppIcon) -> QIcon:
    return QIcon.fromTheme(icon.value)


def get_wizard_pixmap(which: QWizard.WizardPixmap) -> QPixmap:
    return QPixmap(str(get_asset(f"{which}.png")))
