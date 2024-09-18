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

import os
import sys
import platform
import subprocess
from pathlib import Path
from enum import IntEnum
from datetime import datetime, timezone

from PyQt6.QtCore import QSettings, QObject


def open_in_file_browser(file: Path) -> None:
    """Open the given file in the system file browser."""

    if sys.platform == "win32":
        os.startfile(file)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", file])
    else:
        subprocess.Popen(["xdg-open", file])


def add_to_startup(app_id: str) -> None:
    """Add the app to start up on macOS."""

    if platform.system() != "Darwin":
        return

    # Set the paths and filenames
    app_path = f"/Applications/{app_id}.app"
    launch_dir = Path("~/Library/LaunchAgents").expanduser()

    if not launch_dir.exists():
        launch_dir.mkdir()

    plist_path = launch_dir / f"{app_id}.plist"
    plist_path.touch()

    # Create the QSettings object
    settings = QSettings(str(plist_path), QSettings.Format.NativeFormat)

    # Set the launch agent properties
    settings.setValue('Label', app_id)
    settings.setValue('ProgramArguments', app_path)
    settings.setValue('RunAtLoad', True)
    settings.setValue('KeepAlive', False)

    # Save the settings to create the plist file
    settings.sync()


class Time(IntEnum):
    SECOND = 1
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    WEEK = DAY * 7
    MONTH = DAY * 30
    YEAR = DAY * 365


class TimeStrings(QObject):
    def get_name(self, unit: Time, plural: bool) -> str:
        # it's not as simple as appending an 's'
        if plural:
            return self.get_plural_name(unit)

        match unit:
            case Time.SECOND:
                return self.tr("second")
            case Time.MINUTE:
                return self.tr("minute")
            case Time.HOUR:
                return self.tr("hour")
            case Time.DAY:
                return self.tr("day")
            case Time.WEEK:
                return self.tr("week")
            case Time.MONTH:
                return self.tr("month")
            case Time.YEAR:
                return self.tr("year")

    def get_plural_name(self, unit: Time) -> str:
        match unit:
            case Time.SECOND:
                return self.tr("seconds")
            case Time.MINUTE:
                return self.tr("minutes")
            case Time.HOUR:
                return self.tr("hours")
            case Time.DAY:
                return self.tr("days")
            case Time.WEEK:
                return self.tr("weeks")
            case Time.MONTH:
                return self.tr("months")
            case Time.YEAR:
                return self.tr("years")

    @property
    def template(self) -> str:
        return self.tr("{n} {name} ago")


def time_ago(timestamp: datetime) -> str:
    delta = datetime.now(tz=timezone.utc) - timestamp
    s = int(delta.total_seconds())

    def get_human_time(seconds: int, unit: Time) -> str:
        n = seconds // unit
        t = TimeStrings()
        name = t.get_name(unit, n != 1)
        return t.template.format(n=n, name=name)

    previous = Time.SECOND

    for unit in Time:
        if s < unit.value:
            return get_human_time(s, previous)
        previous = unit

    return get_human_time(s, Time.YEAR)
