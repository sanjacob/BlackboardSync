#!/usr/bin/env python3

"""
Blackboard Model Classes
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

from dataclasses import dataclass
from dateutil.parser import isoparse


class SanitisePath:
    _unsafe = ['/', "\\", '<', '>', ':', '"', '|', '?', '*']

    @classmethod
    def get_path(cls, path):
        safe_path = path

        for c in cls._unsafe:
            safe_path = safe_path.replace(c, '_')

        return safe_path


@dataclass(frozen=True)
class BBLocale:
    force: bool = False


@dataclass(frozen=True)
class BBDuration:
    type: str = ""


@dataclass(frozen=True)
class BBEnrollment:
    type: str = ""


@dataclass(frozen=True)
class BBProctoring:
    secureBrowserRequiredToTake: bool = False
    secureBrowserRequiredToReview: bool = False
    webcamRequired: bool = False


@dataclass(frozen=True)
class BBFile:
    fileName: str = ""


@dataclass(frozen=True)
class BBAttachment:
    id: str = ""
    fileName: str = ""
    mimeType: str = ""


class BBContentHandler:
    def __init__(self, id="", url="", file={}, gradeColumnId="", groupContent="",
                 targetId="", targetType="", placementHandle="", assessmentId="", proctoring={}):
        self._id = id
        self._file = None
        if file:
            self._file = BBFile(**file)
        self._url = url
        self._gradeColumnId = gradeColumnId
        self._groupContent = groupContent
        self._targetId = targetId
        self._targetType = targetType
        self._placementHandle = placementHandle
        self._proctoring = BBProctoring(**proctoring)

    @property
    def id(self):
        return self._id

    # Other unhandled file types
    # resource/x-bb-bltiplacement-Portal
    # resource/x-bb-toollink
    # resource/x-bb-courselink

    @property
    def isNone(self) -> bool:
        return not bool(self.id)

    @property
    def isFolder(self) -> bool:
        return self.id == "resource/x-bb-folder"

    @property
    def isFile(self) -> bool:
        return self.id == "resource/x-bb-file"

    @property
    def isDocument(self) -> bool:
        return self.id == "resource/x-bb-document"

    @property
    def isExternalLink(self) -> bool:
        return self.id == "resource/x-bb-externallink"

    @property
    def isToolLink(self) -> bool:
        return self.id == "resource/x-bb-toollink"

    @property
    def isTurnItInAssignment(self) -> bool:
        return self.id == "resource/x-turnitin-assignment"

    @property
    def isPlacement(self) -> bool:
        return self.id == "resource/x-bb-bltiplacement-Portal"

    @property
    def isAssignment(self) -> bool:
        return self.id == "resource/x-bb-assignment"

    @property
    def isTest(self) -> bool:
        return self.id == "resource/x-bb-asmt-test-link"

    @property
    def isSyllabus(self) -> bool:
        return self.id == "resource/x-bb-syllabus"

    @property
    def isCourseLink(self) -> bool:
        return self.id == "resource/x-bb-courselink"

    @property
    def isBlankPage(self) -> bool:
        return self.id == "resource/x-bb-blankpage"

    @property
    def isNotHandled(self) -> bool:
        return (self.isNone or self.isToolLink or self.isTurnItInAssignment or self.isAssignment
                or self.isTest or self.isSyllabus or self.isCourseLink or self.isPlacement
                or self.isBlankPage)

    @property
    def file(self):
        return self._file

    @property
    def url(self):
        return self._url

    @property
    def gradeColumnId(self):
        return self._gradeColumnId

    @property
    def groupContent(self):
        return self._groupContent

    @property
    def targetId(self):
        return self._targetId

    @property
    def targetType(self):
        return self._targetType

    @property
    def placementHandle(self):
        return self._placementHandle

    @property
    def assessmentId(self):
        return self._assessmentId

    @property
    def proctoring(self):
        return self._proctoring


@dataclass(frozen=True)
class BBLink:
    href: str = ""
    rel: str = ""
    title: str = ""
    type: str = ""


class BBAvailability:
    def __init__(self, available="", allowGuests: bool = False, adaptiveRelease={}, duration={}):
        self._available = (available == "Yes")
        self._allowGuests = allowGuests
        self._adaptiveRelease = adaptiveRelease
        self._duration = BBDuration(**duration)

    @property
    def isAvailable(self):
        return self._available

    @property
    def allowGuests(self):
        return self._allowGuests

    @property
    def adaptiveRelease(self):
        return self._adaptiveRelease

    @property
    def duration(self):
        return self._duration


class BBCourseContent:
    def __init__(self, id="", title="", body="", created="", modified="",
                 position: int = 0, hasChildren: bool = False, launchInNewWindow: bool = False,
                 reviewable: bool = False, availability={}, contentHandler={}, links={},
                 hasGradebookColumns: bool = False, hasAssociatedGroups: bool = False):
        self._id = id
        self._title = title
        self._body = body

        self._created = created
        self._modified = modified

        self._position = position
        self._hasChildren = hasChildren

        self._launchInNewWindow = launchInNewWindow
        self._reviewable = reviewable
        self._availability = BBAvailability(**availability)
        self._contentHandler = BBContentHandler(**contentHandler)

        self._links = [BBLink(**link) for link in links]
        self._hasGradebookColumns = hasGradebookColumns
        self._hasAssociatedGroups = hasAssociatedGroups

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def title_safe(self):
        return SanitisePath.get_path(self._title)

    @property
    def body(self):
        return self._body

    @property
    def created(self):
        return self._created

    @property
    def modified(self):
        return self._modified

    @property
    def modifiedDT(self):
        return isoparse(self._modified)

    @property
    def position(self):
        return self._position

    @property
    def hasChildren(self):
        return self._hasChildren

    @property
    def launchInNewWindow(self):
        return self._launchInNewWindow

    @property
    def reviewable(self):
        return self._reviewable

    @property
    def availability(self):
        return self._availability

    @property
    def contentHandler(self):
        return self._contentHandler

    @property
    def links(self):
        return self._links

    @property
    def hasGradebookColumns(self):
        return self._hasGradebookColumns

    @property
    def hasAssociatedGroups(self):
        return self._hasAssociatedGroups


class BBContentChild(BBCourseContent):
    def __init__(self, body="", parentId="", **kwargs):
        super().__init__(**kwargs)
        self._body = body
        self._parentId = parentId

    @property
    def body(self):
        return self._body

    @property
    def parentId(self):
        return self._parentId


class BBMembership:
    def __init__(self, id="", userId="", courseId="", dataSourceId="",
                 created="", modified="", availability={}, courseRoleId="",
                 lastAccessed="", childCourseId=""):
        self._id = id
        self._userId = userId
        self._courseId = courseId
        self._dataSourceId = dataSourceId
        self._created = created
        self._modified = modified
        self._availability = BBAvailability(**availability)
        self._courseRoleId = courseRoleId
        self._lastAccessed = lastAccessed
        self._childCourseId = childCourseId

    @property
    def id(self):
        return self._id

    @property
    def userId(self):
        return self._userId

    @property
    def courseId(self):
        return self._courseId

    @property
    def childCourseId(self):
        return self._childCourseId

    @property
    def dataSourceId(self):
        return self._dataSourceId

    @property
    def created(self):
        return self._created

    @property
    def modified(self):
        return self._modified

    @property
    def modifiedDT(self):
        return isoparse(self._modified)

    @property
    def availability(self):
        return self._availability

    @property
    def courseRoleId(self):
        return self._courseRoleId

    @property
    def lastAccessed(self):
        return self._lastAccessed


class BBCourse:
    def __init__(self, id="", courseId="", name="", description="", modified="",
                 organization: bool = False, ultraStatus="", closedComplete: bool = False,
                 availability={}, enrollment={}, locale={}, externalAccessUrl=""):
        self._id = id
        self._courseId = courseId
        self._name = name
        self._description = description
        self._modified = modified
        self._organization = organization
        self._ultraStatus = ultraStatus
        self._closedComplete = closedComplete
        self._availability = BBAvailability(**availability)
        self._enrollment = BBEnrollment(**enrollment)
        self._locale = BBLocale(**locale)
        self._externalAccessUrl = externalAccessUrl

    @property
    def id(self):
        return self._id

    @property
    def courseId(self):
        return self._courseId

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def modified(self):
        return self._modified

    @property
    def modifiedDT(self):
        return isoparse(self._modified)

    @property
    def organization(self):
        return self._organization

    @property
    def ultraStatus(self):
        return self._ultraStatus

    @property
    def closedComplete(self):
        return self._closedComplete

    @property
    def availability(self):
        return self._availability

    @property
    def externalAccessUrl(self):
        return self._externalAccessUrl


if __name__ == '__main__':
    pass
