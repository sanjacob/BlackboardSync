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
from hypothesis import given, infer
from hypothesis import strategies as st
from pathvalidate import sanitize_filename

from blackboard_sync.blackboard import (BBFile, BBLink, BBCourse, BBLocale,
                                        BBDuration, BBAttachment, BBEnrollment,
                                        BBMembership, BBProctoring,
                                        BBContentChild, BBCourseContent)

from .strategies import bb_resource_type


class TestBBCourseContent:
    def test_content_safe_title(self):
        og_title = "puppy.docx"
        sanitised = og_title

        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_path_safe

    @pytest.mark.parametrize(
        ('title', 'sanitised'),
        (
            pytest.param("a/a\\a<a>a:a\"a|a?a*a.docx", f"{'a_' * 9}a.docx", id="unsafe chars"),
            pytest.param("../../../../important_file",
                         ".._.._.._.._important_file", id="path traversal unix"),
            pytest.param("..\\..\\..\\..\\important_file.exe",
                         ".._.._.._.._important_file.exe", id="path traversal windows")
        )
    )
    def test_content_sanitise_title(self, title, sanitised):
        obj = BBCourseContent(title=title)
        assert obj.title_path_safe == sanitised

    @given(st.text())
    def test_content_sanitise_title_hypothesis(self, filename):
        safe_path = sanitize_filename(filename or 'Title missing', replacement_text='_')
        obj = BBCourseContent(title=filename)
        assert safe_path or '' == obj.title_path_safe
