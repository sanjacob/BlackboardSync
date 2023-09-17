"""
Blackboard Model Classes
"""

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

from enum import Enum
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel, field_validator, ConfigDict
from pathvalidate import sanitize_filename


class ImmutableModel(BaseModel):
    """Model with const attributes."""
    model_config = ConfigDict(frozen=True)


class BBLocale(ImmutableModel):
    force: bool = False


class BBDurationType(str, Enum):
    """Blackboard Course Duration Type."""

    Continuous: str = 'Continuous'
    DateRange: str = 'DateRange'
    FixedNumDays: str = 'FixedNumDays'
    Term: str = 'Term'


class BBDuration(ImmutableModel):
    type: Optional[str] = None


class BBEnrollment(ImmutableModel):
    type: Optional[str] = None


class BBProctoring(ImmutableModel):
    secureBrowserRequiredToTake: bool = False
    secureBrowserRequiredToReview: bool = False
    webcamRequired: bool = False


class BBFile(ImmutableModel):
    """Blackboard File."""

    fileName: Optional[str] = None


class BBAttachment(ImmutableModel):
    """Blackboard File Attachment."""

    id: Optional[str] = None
    fileName: Optional[str] = None
    mimeType: Optional[str] = None


class BBLink(ImmutableModel):
    """Blackboard Link."""

    href: Optional[str] = None
    rel: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None


class BBAvailability(ImmutableModel):
    available: Optional[bool] = None
    allowGuests: bool = False
    adaptiveRelease: dict = {}
    duration: Optional[BBDuration] = None


class BBMembership(ImmutableModel):
    """Blackboard Membership. Represents relation between student and course."""

    id: Optional[str] = None
    userId: Optional[str] = None
    courseId: Optional[str] = None
    dataSourceId: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    availability: Optional[BBAvailability] = None
    courseRoleId: Optional[str] = None
    lastAccessed: Optional[datetime] = None
    childCourseId: Optional[str] = None


class BBResourceType(str, Enum):
    """Different resource types on Blackboard."""

    folder = 'x-bb-folder'
    file = 'x-bb-file'
    document = 'x-bb-document'
    externallink = 'x-bb-externallink'
    toollink = 'x-bb-toollink'
    turnitin_assignment = 'x-turnitin-assignment'
    bltiplacement_portal = 'x-bb-bltiplacement-Portal'
    assignment = 'x-bb-assignment'
    asmt_test_link = 'x-bb-asmt-test-link'
    syllabus = 'x-bb-syllabus'
    courselink = 'x-bb-courselink'
    blankpage = 'x-bb-blankpage'


class BBContentHandler(ImmutableModel):
    id: Union[BBResourceType, str, None] = None
    url: Optional[str] = None
    file: Optional[BBFile] = None
    gradeColumnId: Optional[str] = None
    groupContent: Optional[str] = None
    targetId: Optional[str] = None
    targetType: Optional[str] = None
    placementHandle: Optional[str] = None
    assessmentId: Optional[str] = None
    proctoring: Optional[BBProctoring] = None

    @field_validator('id')
    def resource_parser(cls, v: Union[BBResourceType, str]):
        """Validate and parse an id resource type."""
        return BBResourceType(v.replace('resource/', ''))

    @property
    def is_not_handled(self) -> bool:
        """Return true if resource should not be handled."""
        return self.id not in (BBResourceType.folder, BBResourceType.file,
                               BBResourceType.document, BBResourceType.externallink)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BBResourceType):
            return self.id == other
        elif isinstance(other, str):
            return self.id == BBResourceType(other)
        return False


class BBCourseContent(ImmutableModel):
    """Blackboard Content."""

    id: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    position: int = 0
    hasChildren: bool = False
    launchInNewWindow: bool = False
    reviewable: bool = False
    availability: Optional[BBAvailability] = None
    contentHandler: Optional[BBContentHandler] = None
    links: list[BBLink] = []
    hasGradebookColumns: bool = False
    hasAssociatedGroups: bool = False

    def __str__(self):
        """Title of the course content."""
        return self.title

    @property
    def title_path_safe(self) -> str:
        """Return a path safe version of the title."""
        return sanitize_filename(self.title or 'Title missing',
                                 replacement_text='_') or ''


class BBContentChild(BBCourseContent):
    """Blackboard Content Child."""

    body: Optional[str] = None
    parentId: Optional[str] = None


class BBCourse(ImmutableModel):
    """BlackboardCourse. Represents an academic course."""

    _parse_name = True

    id: Optional[str] = None
    courseId: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    modified: Optional[datetime] = None
    organization: bool = False
    ultraStatus: Optional[str] = None
    closedComplete: bool = False
    availability: Optional[BBAvailability] = None
    enrollment: Optional[BBEnrollment] = None
    locale: Optional[BBLocale] = None
    externalAccessUrl: Optional[str] = None

    @property
    def code(self) -> Optional[str]:
        """Parse course code."""
        if self.name:
            code_split = self.name.split(' : ', 1)
            return code_split[0]
        return None

    @property
    def title(self) -> Optional[str]:
        """Parse course title."""
        if self.name:
            name_split = self.name.split(' : ', 1)[-1].split(',')
            return sanitize_filename(name_split[0], replacement_text='_')
        return None
