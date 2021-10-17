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

import pytest
from blackboard_sync.blackboard.blackboard import BBLocale, BBFile, BBAttachment, BBCourseContent


class TestBBLocale():
    def test_force(self):
        lf = BBLocale(False)
        assert not lf.force

        lt = BBLocale(True)
        assert lt.force


class TestBBFile():
    def test_filename(self):
        doc_name = "example.docx"
        example = BBFile(fileName=doc_name)
        assert example.fileName == doc_name

        empty = BBFile("")
        assert empty.fileName == ""


class TestBBAttachment():
    def test_id(self):
        attm_id = "ID"
        example = BBAttachment(id=attm_id)
        assert example.id == attm_id

        empty = BBAttachment(id="")
        assert empty.id == ""

    def test_filename(self):
        doc_name = "example.docx"
        example = BBAttachment(fileName=doc_name)
        assert example.fileName == doc_name

        empty = BBAttachment(fileName="")
        assert empty.fileName == ""

    def test_mimetype(self):
        mime = "text/html"
        example = BBAttachment(mimeType=mime)
        assert example.mimeType == mime

        empty = BBAttachment(mimeType="")
        assert empty.mimeType == ""


class TestBBCourseContent():
    def test_safe_title(self):
        og_title = "puppy.docx"
        sanitised = og_title

        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_safe

    def test_unsafe_chars(self):
        og_title = "a/a\\a<a>a:a\"a|a?a*a.docx"
        sanitised = f"{'a_' * 9}a.docx"
        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_safe

    def test_dir_escalation_nix(self):
        og_title = "../../../../important_file"
        sanitised = ".._.._.._.._important_file"
        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_safe

    def test_dir_escalation_win(self):
        og_title = "..\\..\\..\\..\\important_file.exe"
        sanitised = ".._.._.._.._important_file.exe"
        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_safe
