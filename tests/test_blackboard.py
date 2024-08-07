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
from pydantic import ValidationError
from hypothesis import given, infer
from hypothesis import strategies as st
from pathvalidate import sanitize_filename

from blackboard_sync.blackboard import (BBFile, BBLink, BBCourse, BBLocale,
                                        BBDuration, BBAttachment, BBEnrollment,
                                        BBMembership, BBProctoring, BBResourceType,
                                        BBContentChild, BBCourseContent, BBContentHandler,
                                        BBAvailable, BBAvailability)

from .strategies import bb_unhandled_resource_type, bb_handled_resource_type, bb_resource_type


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

    @given(bb_resource_type())
    def test_content_handler(self, res_type: str):
        assert BBContentHandler(id=res_type).id in (res_type.split('/')[-1], BBResourceType.other)

    @given(bb_handled_resource_type())
    def test_content_handler_handled(self, res_type: str):
        assert not (BBContentHandler(id=res_type).is_not_handled)

    @given(bb_unhandled_resource_type())
    def test_content_handler_unhandled(self, res_type: str):
        assert BBContentHandler(id=res_type).is_not_handled

    @pytest.mark.parametrize('available', ('Yes', 'No', 'Disabled'))
    def test_bb_available_not_other(self, available: str):
        assert BBAvailable(available) != BBAvailable.Other

    @pytest.mark.parametrize('available', ('UnexpectedValue', 'NotReal'))
    def test_bb_available_other(self, available: str):
        assert BBAvailable(available) == BBAvailable.Other

    @pytest.mark.parametrize('available', ('Yes', 'Term', 'PartiallyVisible' 'UnexpectedValue'))
    def test_bb_available_yes(self, available: str):
        assert BBAvailable(available)

    @pytest.mark.parametrize('available', ('No', 'Disabled'))
    def test_bb_available_no(self, available: str):
        assert not BBAvailable(available)

    @pytest.mark.parametrize('available', (True, False))
    def test_bb_available_bool(self, available: bool):
        assert BBAvailability(available=available).available == BBAvailable.Other
