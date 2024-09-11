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

from typing import NamedTuple
from enum import Enum, IntEnum, auto

from PyQt6.QtWidgets import QSystemTrayIcon


class Event(Enum):
    UPDATE_AVAILABLE = auto()
    DOWNLOAD_STARTED = auto()
    DOWNLOAD_ERROR = auto()


class Severity(Enum):
    NO_ICON = QSystemTrayIcon.MessageIcon.NoIcon
    INFORMATION = QSystemTrayIcon.MessageIcon.Information
    WARNING = QSystemTrayIcon.MessageIcon.Warning
    CRITICAL = QSystemTrayIcon.MessageIcon.Critical


class Duration(IntEnum):
    SHORT = 4
    LONG = 10


class SyncTrayMsg(NamedTuple):
    title: str
    msg: str
    duration: QSystemTrayIcon.MessageIcon
    severity: int


_messages = {
    Event.UPDATE_AVAILABLE: SyncTrayMsg(
        'An update is available',
        'You can update the app from your digital store.',
        Severity.INFORMATION.value, Duration.SHORT
    ),
    Event.DOWNLOAD_STARTED: SyncTrayMsg(
        'The download has started',
        'The app is running in the background.',
        Severity.INFORMATION.value, Duration.SHORT
    ),
    Event.DOWNLOAD_ERROR: SyncTrayMsg(
        'The download could not be completed',
        'There was an error while downloading your content.',
        Severity.WARNING.value, Duration.LONG
    )
}


def get_msg(evt: Event) -> SyncTrayMsg:
    return _messages[evt]
