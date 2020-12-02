 #!/usr/bin/env python3

"""
Blackboard API,
an interface to make
Blackboard API calls

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

import json
import base64
import logging
import requests
from bs4 import BeautifulSoup

class SafeFormat(dict):
    def __missing__(self, key):
        return ''

class BlackboardSession:
    base_url = f"https://portal.uclan.ac.uk"
    fs_url = f"https://fs.uclan.ac.uk"
    bb_session = None

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.NullHandler())

    def __init__(self, user, password):
        if not self.auth(user, password):
            raise ValueError("Login incorrect")

    def auth(self, user, password):
        """
        Go through regular authentication process,
        that is, ask auth server to generate token and then
        provide the token back to the blackboard server

        :param string user: UCLan student email address, including domain
        :param string password: Corresponding password to UCLan account
        """

        # Create requests session to preserve session coookies
        bb_session = requests.Session()

        # Request blackboard landing page to get right url to submit login to
        first_r = bb_session.get(f"{self.base_url}/auth-saml/saml/login?apId=_172_1")
        first_soup = BeautifulSoup(first_r.text, features="lxml")
        login_url = first_soup.find(id="loginForm").get('action')

        # POST login to auth server, it'll respond with a token (or error page)
        auth = {
            'UserName': user,
            'Password': password
        }

        second_r = bb_session.post(f"{self.fs_url}{login_url}", data=auth)

        # Parse base64-encoded token from response
        second_soup = BeautifulSoup(second_r.text, features="lxml")
        hidden_input = second_soup.find("input")

        # If server returns error page, password is incorrect but user exists
        if hidden_input.get("name") != "SAMLResponse":
            # Password did not match username
            self.logger.error(f"Password is incorrect")
            return False

        token_encoded = hidden_input.get('value')

        # Decode it to verify auth was successful
        token_decoded = base64.b64decode(token_encoded)
        token_soup = BeautifulSoup(token_decoded, features="lxml")
        token_status = token_soup.find("samlp:statuscode").get("value")
        auth_status = token_status.split(':')[-1]

        # Return error if token status was not successful (user not found)
        if auth_status != "Success":
            # Username was not found
            self.logger.error(f"Username was not found")
            return False

        # Provide token to blackboard server to finish
        hidden_auth = {
            'SAMLResponse': token_encoded
        }

        final_r = bb_session.post(f"{self.base_url}/auth-saml/saml/SSO/alias/_172_1", data=hidden_auth)
        self.logger.info(f"Auth flow complete")

        self.bb_session = bb_session
        return True

    def get(endpoint, version=1):
        def get_decorator(func):
            def get_wrapper(self, id=None, *args, **kwargs):
                param_endpoint = endpoint.format_map(SafeFormat(kwargs))

                endpoint_format = f"{self.base_url}/learn/api/public/v{version}{param_endpoint}"
                response = self.bb_session.get(endpoint_format, params=kwargs).json()

                if not response:
                    raise ValueError('Server response empty')
                elif 'status' in response:
                    self.logger.error(f"Code {response['status']}: {response['message']}")
                    if response['status'] == 401:
                        raise ValueError('Not authorized')
                    raise ValueError('Server responded with an error code')
                elif 'results' in response:
                    return func(self, response['results'])
                else:
                    return func(self, response)
            return get_wrapper
        return get_decorator

    # announcements #

    # Get Announcement(s)
    @get("/announcements/{announcement_id}")
    def fetchAnnouncements(self, response):
        return response

    # attendance #

    # Get Course Meetings
    @get("/courses/{course_id}/meetings")
    def fetchCourseMeetings(self, response):
        return response

    # Generate Attendance Data Download Url
    @get("/courses/{course_id}/meetings/downloadUrl")
    def fetchAttendanceDataDownloadUrl(self, response):
        return response

    # Get Attendance Records By User Id
    @get("/courses/{course_id}/meetings/users/{user_id}")
    def fetchAttendanceRecordsByUserId(self, response):
        return response

    # Get Course Meeting
    @get("/courses/{course_id}/meetings/{meeting_id}")
    def fetchCourseMeeting(self, response):
        return response

    # Get Attendance Records By Meeting Id / Get Attendance Record
    @get("/courses/{course_id}/meetings/{meeting_id}/users/{user_id}")
    def fetchAttendanceRecordsByMeetingId(self, response):
        return response

    # calendar #

    # Get Calendars
    @get("/calendars/")
    def fetchCalendar(self, response):
        return response

    # Get Calendar Item(s)
    @get("/calendars/items/{calendar_item_type}/{calendar_item_id}")
    def fetchCalendarItems(self, response):
        return response

    # content #

    # Get Content(s)
    @get("/courses/{course_id}/contents/{content_id}")
    def fetchContents(self, response):
        return response

    # Get Content Children
    @get("/courses/{course_id}/contents/{content_id}/children")
    def fetchContentChildren(self, response):
        return response

    # content file attachments #

    # Get File Attachment(s)
    @get("/courses/{course_id}/contents/{content_id}/attachments/{attachment_id}")
    def fetchFileAttachments(self, response):
        return response

    # Get File Attachment(s)
    @get("/courses/{course_id}/contents/{content_id}/attachments/{attachment_id}/download")
    def download(self, response):
        return response

    # content group assignments #

    # Get Content Group(s)
    @get("/courses/{course_id}/contents/{content_id}/groups/{group_id}")
    def fetchContentGroups(self, response):
        return response

    # content resources #

    # Get Course Resource(s)
    @get("/courses/{course_id}/resources/{resource_id}")
    def fetchCourseResources(self, response):
        return response

    # Get Course Resource Children
    @get("/courses/{course_id}/resources/{resource_id}/children")
    def fetchCourseResourceChildren(self, response):
        return response

    # content review #

    # Get Review Status(s)
    @get("/courses/{course_id}/contents/{content_id}/users/{user_id}/reviewStatus")
    def fetchReviewStatus(self, response):
        return response

    # course announcements #

    # Get Course Announcement(s)
    @get("/courses/{course_id}/announcements/{announcement_id}")
    def fetchCourseAnnouncements(self, response):
        return response

    # course assessments #

    # Get Course Assessments Question(s)
    @get("/courses/{course_id}/assessments/{assessment_id}/questions/{question_id}")
    def fetchQuestions(self, response):
        return response

    # course categories #

    # Get Categorie(s)
    @get("/catalog/categories/{category_type}/{category_id}")
    def fetchCategory(self, response):
        return response

    # Get Membership(s)
    @get("/catalog/categories/{category_type}/{category_id}/courses/{course_id}")
    def fetchMemberships(self, response):
        return response

    # Get Child Categories
    @get("/catalog/categories/{category_type}/{parent_id}/children")
    def fetchChildCategories(self, response):
        return response

    # Get Memberships
    @get("/courses/{course_id}/categories")
    def fetchCategories(self, response):
        return response

    # course grade attempts #

    # Get Attempt File Meta Data (List)
    @get("/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}")
    def fetchAttemptFileMetaData(self, response):
        return response

    # Get Attempt File Meta Data (List)
    @get("/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}/download")
    def downloadAttemptFileMetaData(self, response):
        return response

    # course grade notations #

    # Get Grade Notation(s)
    @get("/courses/{course_id}/gradebook/gradeNotations/{grade_notation_id}")
    def fetchGradeNotations(self, response):
        return response

    # course gradebook categories #

    # Get Gradebook Categori(es)
    @get("/courses/{course_id}/gradebook/categories/{category_id}")
    def fetchGradebookCategories(self, response):
        return response

    # course grades #

    # Get Grade Schema(s)
    @get("/courses/{course_id}/gradebook/schemas/{schema_id}")
    def fetchGradeSchemas(self, response):
        return response

    # Get Grade Column(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}", 2)
    def fetchGradeColumns(self, response):
        return response

    # Get Grade Column Attempt(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}/attempts/{attempt_id}", 2)
    def fetchColumnAttempts(self, response):
        return response

    # Get Column Grade(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}/users/{user_id}", 2)
    def fetchColumnGrades(self, response):
        return response

    # Get Column Grades Last Changed
    @get("/courses/{course_id}/gradebook/columns/{column_id}/users/last_changed", 2)
    def fetchColumnGradeLastChanged(self, response):
        return response

    # Get User Grades
    @get("/courses/{course_id}/gradebook/users/{user_id}", 2)
    def fetchUserGrades(self, response):
        return response

    # course grading periods #

    # Get Grading Period(s)
    @get("/courses/{course_id}/gradebook/periods/{period_id}")
    def fetchGradingPeriods(self, response):
        return response

    # course group users #

    # Get Group Memberships
    @get("/courses/{course_id}/groups/{group_id}/users/{user_id}", 2)
    def fetchGroupMemberships(self, response):
        return response

    # course groups #

    # Get Group(s)
    @get("/courses/{course_id}/groups/{group_id}", 2)
    def fetchGroups(self, response):
        return response

    # Get Group Set(s)
    @get("/courses/{course_id}/groups/sets/{group_id}", 2)
    def fetchGroupSets(self, response):
        return response

    # Get Group Set Children
    @get("/courses/{course_id}/groups/sets/{group_id}/groups", 2)
    def fetchGroupSetChildren(self, response):
        return response

    # course memberships #

    # Get Course Membership(s)
    @get("/courses/{course_id}/users/{user_id}")
    def fetchCourseMemberships(self, response):
        return response

    # Get User Memberships
    @get("/users/{user_id}/courses")
    def fetchUserMemberships(self, response):
        return response

    # courses #

    # Get Course Child(ren)
    @get("/courses/{course_id}/children/{child_course_id}")
    def fetchCourseChildren(self, response):
        return response

    # Get Cross List Set
    @get("/courses/{course_id}/crossListSet")
    def fetchCrossListSet(self, response):
        return response

    # Get Task
    @get("/courses/{course_id}/tasks/{task_id}")
    def fetchTask(self, response):
        return response

    # Get Course(s)
    @get("/courses/{course_id}", 3)
    def fetchCourses(self, response):
        return response

    # data sources #

    # Get Data Source(s)
    @get("/dataSources/{data_source_id}")
    def fetchDataSources(self, response):
        return response

    # institutional hierarchy #

    # Get Associated Nodes
    @get("/courses/{course_id}/nodes")
    def fetchAssociatedNodes(self, response):
        return response

    # Get Node(s)
    @get("/institutionalHierarchy/nodes/{node_id}")
    def fetchNodes(self, response):
        return response

    # Get Node Children
    @get("/institutionalHierarchy/nodes/{node_id}/children")
    def fetchNodeChildren(self, response):
        return response

    # Get Node Course Associations
    @get("/institutionalHierarchy/nodes/{node_id}/courses")
    def fetchNodeCourseAssociations(self, response):
        return response

    # lti #

    # Get Placement(s)
    @get("/lti/placements/{placement_id}")
    def fetchPlacements(self, response):
        return response

    # Get Domain Config(s)
    @get("/lti/domains/{domain_id}")
    def fetchDomainConfig(self, response):
        return response

    # performance dashboard #

    # Get Review Status By Course Id
    @get("/courses/{course_id}/performance/contentReviewStatus")
    def fetchReviewStatus(self, response):
        return response

    # proctoring #

    # Get Proctoring Service(s)
    @get("/proctoring/services/{service_id}")
    def fetchProctoringServices(self, response):
        return response

    # roles #

    # Get Course Role(s)
    @get("/courseRoles/{role_id}")
    def fetchCourseRoles(self, response):
        return response

    # Get Institution Role(s)
    @get("/institutionRoles/{role_id}")
    def fetchInstitutionRoles(self, response):
        return response

    # Get System Role(s)
    @get("/systemRoles/{role_id}")
    def fetchSystemRoles(self, response):
        return response

    # sessions #

    # Get Active Sessions
    @get("/sessions")
    def fetchSessions(self, response):
        return response

    # SIS logs #

    # Get SIS Logs By Data Set Uid
    @get("/logs/sis/dataSets/{id}")
    def fetchSISLogs(self, response):
        return response

    # system #

    # Get Policies
    @get("/system/policies/privacy")
    def fetchPolicies(self, response):
        return response

    # Get System Task
    @get("/system/tasks/{task_id}")
    def fetchSystemTask(self, response):
        return response

    # Get Version
    @get("/system/version")
    def fetchVersion(self, response):
        return response

    # terms #

    # Get Term(s)
    @get("/terms/{term_id}")
    def fetchTerms(self, response):
        return response

    # uploads #

    # users #

    # Get Users(s)
    @get("/users/{user_id}")
    def fetchUsers(self, response):
        return response

    # Get Users Avatar
    @get("/users/{user_id}/avatar")
    def fetchAvatar(self, response):
        return response

    # Get Observees
    @get("/users/{user_id}/observees")
    def fetchObservees(self, response):
        return response

    # Get Observers
    @get("/users/{user_id}/observers")
    def fetchObservers(self, response):
        return response

    # Get Current Active User By Id
    @get("/users/{user_id}/sessions")
    def fetchCurrentActiveUser(self, response):
        return response


def main():
    print("Blackboard API, import from script to use")


if __name__ == '__main__':
    main()
