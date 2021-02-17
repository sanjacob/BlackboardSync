#!/usr/bin/env python3

"""
BlackboardSync Tests
Copyright (C) 2020
Jacob Sánchez Pérez
"""

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

import sys
import unittest
from PyQt5.QtWidgets import QApplication, QStyleFactory
from qt.qt_elements import SettingsWindow, LoginWindow, SyncTrayIcon


class TestAllWindows(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create("Fusion"))

    def test_windows(self):
        self.login_window = LoginWindow()
        self.settings_window = SettingsWindow()
        self.login_window.show()
        self.settings_window.show()
        self.app.exec()

    def test_tray(self):
        self.tray = SyncTrayIcon()
        self.tray.quit_signal.connect(self.app.quit)
        self.app.exec()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
