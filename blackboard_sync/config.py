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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
import configparser
from typing import Any, Optional
from pathlib import Path
from functools import wraps
from datetime import datetime
from collections.abc import Callable

import keyring
from appdirs import user_config_dir

from .__about__ import __author__


class Config(configparser.ConfigParser):
    _file_exists = False
    _logger = logging.getLogger(__name__)

    def __init__(self, config_file: Path, *args, **kwargs):
        super().__init__(converters={'path': Path, 'date': datetime.fromisoformat},
                         interpolation=None, *args, **kwargs)
        self._config_file = config_file
        self.read(self._config_file)

        # Set up logging
        self.logger.setLevel(logging.WARN)
        self.logger.addHandler(logging.StreamHandler())

    def save(self):
        with self._config_file.open('w') as config_file:
            self.write(config_file)

    @staticmethod
    def persist(func) -> Callable[[Any, Any], None]:
        @wraps(func)
        def save_wrapper(self, *args: Any, **kwargs: Any) -> None:
            func(self, *args, **kwargs)
            self.save()
            self.logger.info("Updated configuration file")
        return save_wrapper

    @property
    def logger(self) -> logging.Logger:
        """Logger for BlackboardSync Configuration, set at level WARN."""
        return self._logger


class SyncConfig(Config):
    """
    Manages Sync Settings
    """
    _config_filename = "blackboard_sync"

    def __init__(self, custom_dir=None):
        config_dir = custom_dir or Path(user_config_dir(appauthor=__author__, roaming=True))
        super().__init__(config_dir / self._config_filename, empty_lines_in_values=False)

        if 'Login' not in self:
            self['Login'] = {}

        if 'Sync' not in self:
            self['Sync'] = {}

        self._login = self['Login']
        self._sync = self['Sync']

    @property
    def last_sync_time(self) -> Optional[datetime]:
        return self._sync.getdate('last_sync_time')

    @last_sync_time.setter
    @Config.persist
    def last_sync_time(self, last: datetime) -> None:
        self._sync['last_sync_time'] = last.isoformat()

    @property
    def download_location(self) -> Optional[Path]:
        return self._sync.getpath('download_location')

    @download_location.setter
    @Config.persist
    def download_location(self, sync_dir: Path) -> None:
        self._sync['download_location'] = str(sync_dir)

    @property
    def username(self) -> Optional[str]:
        return self._login.get('username')

    @username.setter
    @Config.persist
    def username(self, user: str) -> None:
        self._login['username'] = user

    @property
    def password(self) -> Optional[str]:
        if self.username is not None:
            return keyring.get_password(self._config_filename, self.username)

    def set_login(self, username: str, password: str) -> None:
        self.username = username
        keyring.set_password(self._config_filename, username, password)
