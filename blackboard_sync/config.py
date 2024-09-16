"""
BlackboardSync configuration manager
"""

# Copyright (C) 2021, Jacob Sánchez Pérez

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

import logging
import configparser
from typing import Any
from pathlib import Path
from functools import wraps
from datetime import datetime
from collections.abc import Callable

from appdirs import user_config_dir

from .__about__ import __author__

logger = logging.getLogger(__name__)


class Config(configparser.ConfigParser):
    """Base configuration manager class, which wraps a ConfigParser."""

    def __init__(self, config_file: Path, *args, **kwargs):
        converters: dict[str, Callable[[str], Any]] = {
            'path': Path, 'date': datetime.fromisoformat
        }

        super().__init__(converters=converters, interpolation=None,
                         *args, **kwargs)

        self._config_file = config_file
        self.read(self._config_file)

        # Set up logging
        logger.setLevel(logging.WARN)
        logger.addHandler(logging.StreamHandler())

    def save(self) -> None:
        """Save the current configuration to disk."""
        with self._config_file.open('w') as config_file:
            self.write(config_file)

    @staticmethod
    def persist(func) -> Callable[[Any, Any], None]:
        """A decorator to save any changes to the field to disk."""
        @wraps(func)
        def save_wrapper(self, *args: Any, **kwargs: Any) -> None:
            func(self, *args, **kwargs)
            self.save()
            logger.info("Updated configuration file")
        return save_wrapper


class SyncConfig(Config):
    """Configuration manager for BlackboardSync."""
    _config_filename = "blackboard_sync"

    def __init__(self, custom_dir=None):
        default_dir = Path(user_config_dir(appauthor=__author__, roaming=True))

        config_dir = custom_dir or default_dir
        super().__init__(config_dir / self._config_filename,
                         empty_lines_in_values=False)

        if 'Sync' not in self:
            self['Sync'] = {}

        self._sync = self['Sync']

    @property
    def last_sync_time(self) -> datetime | None:
        return self._sync.getdate('last_sync_time')

    @last_sync_time.setter
    @Config.persist
    def last_sync_time(self, last: datetime | None) -> None:
        if last is None:
            self.remove_option('Sync', 'last_sync_time')
        else:
            self._sync['last_sync_time'] = last.isoformat()

    @property
    def download_location(self) -> Path | None:
        # Default download location
        default = Path(Path.home(), 'Downloads', 'BlackboardSync')
        return self._sync.getpath('download_location') or default

    @download_location.setter
    @Config.persist
    def download_location(self, sync_dir: Path) -> None:
        self._sync['download_location'] = str(sync_dir)

    @property
    def university_index(self) -> int | None:
        return self._sync.getint('university')

    @university_index.setter
    @Config.persist
    def university_index(self, university: int) -> None:
        self._sync['university'] = str(university)

    @property
    def min_year(self) -> int | None:
        return self._sync.getint('min_year')

    @min_year.setter
    @Config.persist
    def min_year(self, year: int | None) -> None:
        self._sync['min_year'] = str(year or 0)
