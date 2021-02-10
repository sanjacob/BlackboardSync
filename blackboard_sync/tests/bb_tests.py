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

import unittest
from blackboard.blackboard import BBLocale, BBFile, BBAttachment


class TestBBLocale(unittest.TestCase):

    def test_force(self):
        lf = BBLocale(False)
        self.assertEqual(lf.force, False, "Should be False")

        lt = BBLocale(True)
        self.assertEqual(lt.force, True, "Should be True")


class TestBBFile(unittest.TestCase):

    def test_fileName(self):
        doc_name = "example.docx"
        example = BBFile(fileName=doc_name)
        self.assertEqual(example.fileName, doc_name, f"Should be {doc_name}")

        empty = BBFile("")
        self.assertEqual(empty.fileName, "", "Should be empty")


class TestBBAttachment(unittest.TestCase):
    def test_id(self):
        attm_id = "ID"
        example = BBAttachment(id=attm_id)
        self.assertEqual(example.id, attm_id, f"Should be {attm_id}")

        empty = BBAttachment(id="")
        self.assertEqual(empty.id, "", "Should be empty")

    def test_fileName(self):
        doc_name = "example.docx"
        example = BBAttachment(fileName=doc_name)
        self.assertEqual(example.fileName, doc_name, f"Should be {doc_name}")

        empty = BBAttachment(fileName="")
        self.assertEqual(empty.fileName, "", "Should be empty")

    def test_mimeType(self):
        mime = "text/html"
        example = BBAttachment(mimeType=mime)
        self.assertEqual(example.mimeType, mime, f"Should be {mime}")

        empty = BBAttachment(mimeType="")
        self.assertEqual(empty.mimeType, "", "Should be empty")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
