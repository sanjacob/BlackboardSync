#!/usr/bin/env python3

"""BlackboardSync Tests"""

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

import unittest
from getpass import getpass
from blackboard_sync.blackboard.api import SafeFormat, BlackboardSession

user = ""
password = ""


class TestSafeFormat():

    def test_missing(self):
        safe_dict = SafeFormat({'a': 1})
        assert safe_dict['b'] == ''

    def test_present(self):
        safe_dict = SafeFormat({'a': 1})
        assert safe_dict['a'] == 1


class TestAPI(unittest.TestCase):

    def test_empty_user(self):
        with self.assertRaises(ValueError):
            BlackboardSession('', 'password')

    def test_empty_login(self):
        with self.assertRaises(ValueError):
            BlackboardSession('', '')

    def test_example_user(self):
        with self.assertRaises(ValueError):
            BlackboardSession('example@uclan.ac.uk', 'password')

    def test_nonexistent_user(self):
        with self.assertRaises(ValueError):
            BlackboardSession('zzzzzzzzzz@uclan.ac.uk', 'password')

    def test_real_user(self):
        with self.assertRaises(ValueError):
            #  as long as you don't have 'password' as password...
            BlackboardSession(user, 'password')

    def test_correct_login(self):
        try:
            BlackboardSession(user, password)
        except ValueError:
            self.fail('User credentials were not valid (maybe you mistyped them?)')


def main():
    global user, password

    print("To run these tests successfully you will need a valid login")
    user = input("Enter your UCLan mail: ")
    password = getpass("Enter your password: ")
    unittest.main()


if __name__ == '__main__':
    main()
