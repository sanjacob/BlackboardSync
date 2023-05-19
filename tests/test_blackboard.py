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


class TestBlackboard:
    @given(st.builds(BBLocale, force=infer))
    def test_bblocale(self, instance):
        print(instance.dict())

    @given(st.builds(BBCourse, id=infer, courseId=infer, description=infer, modified=infer,
                     organization=infer, ultraStatus=infer, closedComplete=infer,
                     availability=infer, enrollment=infer, locale=infer,
                     externalAccessUrl=infer, name=bb_resource_type()))
    def test_bb_course(self, instance):
        print(instance.dict())


@pytest.mark.skip
class TestBBDataclasses:
    @given(st.booleans())
    def test_bblocale(self, force):
        obj = BBLocale(force=force)
        assert obj.force == force

    @given(st.text())
    def test_bbduration(self, bb_type):
        obj = BBDuration(type=bb_type)
        assert obj.type == bb_type

    @given(st.text())
    def test_bbenrollment(self, bb_type):
        obj = BBEnrollment(type=bb_type)
        assert obj.type == bb_type

    @given(st.booleans(), st.booleans(), st.booleans())
    def test_bbproctoring(self, sb_to_take, sb_to_review, webcam_required):
        obj = BBProctoring(secureBrowserRequiredToTake=sb_to_take,
                           secureBrowserRequiredToReview=sb_to_review,
                           webcamRequired=webcam_required)
        assert obj.secureBrowserRequiredToTake == sb_to_take
        assert obj.secureBrowserRequiredToReview == sb_to_review
        assert obj.webcamRequired == webcam_required

    @given(st.text())
    def test_bbfile(self, filename):
        obj = BBFile(fileName=filename)
        assert obj.fileName == filename

    @given(st.text(), st.text(), st.text())
    def test_bbattachment(self, id, filename, mimetype):
        obj = BBAttachment(id=id, fileName=filename, mimeType=mimetype)
        assert obj.id == id
        assert obj.fileName == filename
        assert obj.mimeType == mimetype

    @given(st.text(), st.text(), st.text(), st.text())
    def test_bblink(self, href, rel, title, bb_type):
        obj = BBLink(href=href, rel=rel, title=title, type=bb_type)
        assert obj.href == href
        assert obj.rel == rel
        assert obj.title == title
        assert obj.type == bb_type

    def test_bbcontenthandler():
        pass

    # @given(st.text(), st.booleans(), st.dictionaries())
    # def test_bbavailability():
    #     pass

    @pytest.mark.skip()
    def test_bbcoursecontent():
        pass

    @given(st.text(), st.text())
    def test_bbcontentchild(self, body, parent_id):
        obj = BBContentChild(body=body, parentId=parent_id)
        # needs work
        assert obj.body == body
        assert obj.parentId == parent_id

    @pytest.mark.skip
    @given(st.text(), st.text(), st.text(), st.text(), st.text(), st.text(), st.text(), st.text(),
           st.text())
    def test_bbmembership(self, id, user_id, course_id, data_source_id,
                          created, modified, course_role_id,
                          last_accessed, child_course_id):
        obj = BBMembership(id=id, userId=user_id, courseId=course_id, dataSourceId=data_source_id,
                           created=created, modified=modified, courseRoleId=course_role_id,
                           lastAccessed=last_accessed, childCourseId=child_course_id)

        assert obj.id == id
        assert obj.userId == user_id
        assert obj.courseId == course_id
        assert obj.dataSourceId == data_source_id
        assert obj.created == created
        assert obj.modified == modified
        assert obj.courseRoleId == course_role_id
        assert obj.lastAccessed == last_accessed
        assert obj.childCourseId == child_course_id

    @given(st.text(), st.text(), st.text(), st.text(), st.text(), st.booleans(), st.text(),
           st.booleans(), st.text())
    def test_bbcourse(self, id, course_id, name, desc, modified, org, ultra_status, closed_complete,
                      external_url):
        obj = BBCourse(id=id, courseId=course_id, name=name, description=desc, modified=modified,
                       organization=org, ultraStatus=ultra_status, closedComplete=closed_complete,
                       externalAccessUrl=external_url)
        assert obj.id == id
        assert obj.courseId == course_id
        assert obj.name == name
        assert obj.description == desc
        assert obj.modified == modified
        assert obj.organization == org
        assert obj.ultraStatus == ultra_status
        assert obj.closedComplete == closed_complete
        assert obj.externalAccessUrl == external_url


@pytest.mark.skip
class TestBBCourseContent:
    def test_content_safe_title(self):
        og_title = "puppy.docx"
        sanitised = og_title

        cc = BBCourseContent(title=og_title)
        assert sanitised == cc.title_safe

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
        assert obj.title_safe == sanitised

    @given(st.text())
    def test_content_sanitise_title_hypothesis(self, filename):
        safe_path = sanitize_filename(filename, replacement_text='_')
        obj = BBCourseContent(title=filename)
        assert safe_path == obj.title_safe
