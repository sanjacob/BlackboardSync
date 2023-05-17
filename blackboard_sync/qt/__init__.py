"""
BlackboardSync Qt GUI.

~~~~~~~~~~~~~~~~~~~~~

A graphical interface using Qt for BlackboardSync.

Basic usage:
    >>> from qt import LoginWindow
    >>> w = LoginWindow()


Full documentation available at <https://blackboardsync.readthedocs.io>.

:copyright: (c) 2021, Jacob Sánchez Pérez.
:license: GPL v2.0, see LICENSE for more details.
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
# Also available at https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

from .qt_elements import (SyncPeriod, SetupWizard, LoginWebView, SyncTrayIcon,
                          SyncTrayMenu, SettingsWindow, RedownloadDialog,
                          UniNotSupportedDialog, OSUtils, UpdateFoundDialog)

__all__ = ['SyncPeriod', 'SetupWizard', 'LoginWebView', 'SyncTrayIcon', 'SyncTrayMenu',
           'SettingsWindow', 'RedownloadDialog', 'UniNotSupportedDialog', 'OSUtils', 'UpdateFoundDialog']
