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
        self.login_window.login_signal.connect(self.logging_in)
        self.settings_window.log_out_signal.connect(self.log_out_clicked)
        self.settings_window.save_signal.connect(self.settings_saved)
        self.app.exec()

    # @unittest.skip("Skip for now")
    def test_tray(self):
        self.tray = SyncTrayIcon()
        self.tray.quit_signal.connect(self.app.quit)
        self.tray.login_signal.connect(self.login_clicked)
        self.tray.settings_signal.connect(self.settings_clicked)
        self.tray.sync_signal.connect(self.sync_clicked)
        self.tray.activated.connect(self.tray_activated)
        self.app.exec()

    def login_clicked(self):
        print("Login entry clicked")
        self.tray.set_logged_in(True)

    def log_out_clicked(self):
        print("Logout entry clicked")

    def sync_clicked(self):
        print("Sync entry clicked")

    def settings_clicked(self):
        print("Settings entry clicked")

    def settings_saved(self):
        print("Settings saved")

    def logging_in(self):
        print("Logging in")

    def tray_activated(self):
        # Reason not specified
        print("Tray activated")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
