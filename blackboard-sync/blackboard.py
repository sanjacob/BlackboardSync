 #!/usr/bin/env python3

"""
Blackboard Wrapper Classes,
an interface to handle API responses

Copyright (C) 2020
Jacob Sánchez Pérez
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License v2
# as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License v2
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.


class BBLocale:
    def __init__(self, force=False):
        self._force = force

    @property
    def force(self):
        return self._force


class BBDuration:
    def __init__(self, type=""):
        self._type = type

    @property
    def type(self):
        return self._type


class BBEnrollment:
    def __init__(self, type=""):
        self._type = type

    @property
    def type(self):
        return self._type


class BBFile:
    def __init__(self, fileName=""):
        self._fileName = fileName

    @property
    def fileName(self):
        return self._fileName


class BBContentHandler:
    def __init__(self, id="", url="", file={}, gradeColumnId="", groupContent="",
                 targetId="", targetType="", placementHandle=""):
        self._id = id
        self._file = BBFile(**file)
        self._url = url
        self._gradeColumnId = gradeColumnId
        self._groupContent = groupContent
        self._targetId = targetId
        self._targetType = targetType
        self._placementHandle = placementHandle

    @property
    def id(self):
        return self._id

    @property
    def isFolder(self):
        return self.id == "resource/x-bb-folder"

    @property
    def isDocument(self):
        return self.id == "resource/x-bb-document"

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


class BBLink:
    def __init__(self, href="", rel="", title="", type=""):
        self._href = href
        self._rel = rel
        self._title = title
        self._type = type

    @property
    def href(self):
        return self._href

    @property
    def rel(self):
        return self._rel

    @property
    def title(self):
        return self._title

    @property
    def type(self):
        return self._type


class BBAvailability:
    def __init__(self, available="", allowGuests=False, adaptiveRelease={},
                 duration={}):
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
                 position=0, hasChildren=False, launchInNewWindow=False,
                 reviewable=False, availability={}, contentHandler={}, links={},
                 hasGradebookColumns=False, hasAssociatedGroups=False):
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
    def title_nb(self):
        return self._title.replace('/', '_')

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
    def availability(self):
        return self._availability

    @property
    def courseRoleId(self):
        return self._courseRoleId

    @property
    def lastAccessed(self):
        return self._lastAccessed


class BBCourse:
    def __init__(self, id="", courseId="", name="", description="",
                 modified="", organization=False, ultraStatus="", closedComplete=False,
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
