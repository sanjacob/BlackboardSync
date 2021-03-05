#!/usr/bin/env python3

"""
Blackboard API,
an interface to make Blackboard API calls on a session basis
"""

# Copyright (C) 2021, Jacob Sánchez Pérez

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

import base64
import logging
import requests
from bs4 import BeautifulSoup


class SafeFormat(dict):
    """Custom dictionary object

    Needed to safely format endpoint strings with placeholders
    without having all parameters (those not present will be left blank)
    """

    def __missing__(self, key):
        return ''


class BlackboardSession:
    """Represents a user session in Blackboard"""

    _base_url = "https://portal.uclan.ac.uk"
    _fs_url = "https://fs.uclan.ac.uk"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())

    def __init__(self, user: str, password: str):
        self._bb_session = None
        self._username = ""
        self._timeout = 12

        if not self.auth(user, password):
            raise ValueError("Login incorrect")

    def auth(self, user: str, password: str) -> bool:
        """
        Go through regular authentication process,
        i.e. ask auth server to generate token and then
        provide the token back to the blackboard server

        :param string user: UCLan student email address,
        :param string password: Password of said account
        """

        # Create requests session to preserve session coookies
        bb_session = requests.Session()

        # Request blackboard landing page to get right url to submit login to
        first_r = bb_session.get(f"{self._base_url}/auth-saml/saml/login?apId=_172_1")
        first_soup = BeautifulSoup(first_r.text, features="lxml")
        login_url = first_soup.find(id="loginForm").get('action')

        # POST login to auth server, it'll respond with a token (or error page)
        auth = {
            'UserName': user,
            'Password': password
        }

        second_r = bb_session.post(f"{self._fs_url}{login_url}", data=auth)

        # Parse base64-encoded token from response
        second_soup = BeautifulSoup(second_r.text, features="lxml")
        hidden_input = second_soup.find("input")

        # If server returns error page, password is incorrect but user exists
        if hidden_input.get("name") != "SAMLResponse":
            # Password did not match username
            self.logger.error("Password is incorrect")
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
            self.logger.error("Username was not found")
            return False

        # Provide token to blackboard server to finish
        hidden_auth = {
            'SAMLResponse': token_encoded
        }

        bb_session.post(f"{self._base_url}/auth-saml/saml/SSO/alias/_172_1", data=hidden_auth)
        self.logger.info("Auth flow complete")

        self._bb_session = bb_session
        self._username = f"userName:{user.split('@')[0]}"
        return True

    def get(endpoint, version=1, json: bool = True, **g_kwargs):
        """Returns a decorator (needed to use fancy @get(...) notation)

        :param string endpoint: Endpoint to make API call to, including placeholders
        :param int version: Version of the BB API used at endpoint (used as part of url)
        :param bool json: If false, returns raw requests response, otherwise returns JSON Object
        :param dict g_kwargs: Any argument in this parameter will be passed on to the requests call
        """

        def get_decorator(func):
            """Returns wrapped function

            :param function func: Function to decorate
            """

            def get_wrapper(self, id=None, *args, **kwargs):
                """Wraps function in REST API call

                :param any id: Not in current use
                :param list args: Not in current use
                :param dict kwargs: Any contents will be passed as request parameters
                """
                param_endpoint = endpoint.format_map(SafeFormat(kwargs))

                endpoint_format = f"{self._base_url}/learn/api/public/v{version}{param_endpoint}"
                if endpoint_format[-1] == "/":
                    endpoint_format = endpoint_format[:-1]

                self.logger.debug(f"Making request to {endpoint_format}")
                response = self._bb_session.get(endpoint_format, params=kwargs,
                                                timeout=self._timeout, **g_kwargs)

                if json:
                    response = response.json()
                else:
                    return func(self, response)

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

    @property
    def username(self) -> str:
        return self._username

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, t: int) -> None:
        self._timeout = t

    # API CALLS
    # https://developer.blackboard.com/portal/displayApi

    # announcements #

    # Get Announcement(s)
    @get("/announcements/{announcement_id}")
    def fetch_announcements(self, response):
        return response

    # attendance #

    # Get Course Meetings
    @get("/courses/{course_id}/meetings")
    def fetch_course_meetings(self, response):
        return response

    # Generate Attendance Data Download Url
    @get("/courses/{course_id}/meetings/downloadUrl")
    def fetch_attendance_data_download_url(self, response):
        return response

    # Get Attendance Records By User Id
    @get("/courses/{course_id}/meetings/users/{user_id}")
    def fetch_attendance_records_by_user_id(self, response):
        return response

    # Get Course Meeting
    @get("/courses/{course_id}/meetings/{meeting_id}")
    def fetch_course_meeting(self, response):
        return response

    # Get Attendance Records By Meeting Id / Get Attendance Record
    @get("/courses/{course_id}/meetings/{meeting_id}/users/{user_id}")
    def fetch_attendance_records_by_meeting_id(self, response):
        return response

    # calendar #

    # Get Calendars
    @get("/calendars/")
    def fetch_calendar(self, response):
        return response

    # Get Calendar Item(s)
    @get("/calendars/items/{calendar_item_type}/{calendar_item_id}")
    def fetch_calendar_items(self, response):
        return response

    # content #

    # Get Content(s)
    @get("/courses/{course_id}/contents/{content_id}")
    def fetch_contents(self, response):
        return response

    # Get Content Children
    @get("/courses/{course_id}/contents/{content_id}/children")
    def fetch_content_children(self, response):
        return response

    # content file attachments #

    # Get File Attachment(s)
    @get("/courses/{course_id}/contents/{content_id}/attachments/{attachment_id}")
    def fetch_file_attachments(self, response):
        return response

    # Get File Attachment(s)
    @get("/courses/{course_id}/contents/{content_id}/attachments/{attachment_id}/download",
         json=False, stream=True)
    def download(self, response):
        return response

    # content group assignments #

    # Get Content Group(s)
    @get("/courses/{course_id}/contents/{content_id}/groups/{group_id}")
    def fetch_content_groups(self, response):
        return response

    # content resources #

    # Get Course Resource(s)
    @get("/courses/{course_id}/resources/{resource_id}")
    def fetch_course_resources(self, response):
        return response

    # Get Course Resource Children
    @get("/courses/{course_id}/resources/{resource_id}/children")
    def fetch_course_resource_children(self, response):
        return response

    # content review #

    # Get Review Status(s)
    @get("/courses/{course_id}/contents/{content_id}/users/{user_id}/reviewStatus")
    def fetch_review_status(self, response):
        return response

    # course announcements #

    # Get Course Announcement(s)
    @get("/courses/{course_id}/announcements/{announcement_id}")
    def fetch_course_announcements(self, response):
        return response

    # course assessments #

    # Get Course Assessments Question(s)
    @get("/courses/{course_id}/assessments/{assessment_id}/questions/{question_id}")
    def fetch_questions(self, response):
        return response

    # course categories #

    # Get Categorie(s)
    @get("/catalog/categories/{category_type}/{category_id}")
    def fetch_category(self, response):
        return response

    # Get Membership(s)
    @get("/catalog/categories/{category_type}/{category_id}/courses/{course_id}")
    def fetch_memberships(self, response):
        return response

    # Get Child Categories
    @get("/catalog/categories/{category_type}/{parent_id}/children")
    def fetch_child_categories(self, response):
        return response

    # Get Memberships
    @get("/courses/{course_id}/categories")
    def fetch_categories(self, response):
        return response

    # course grade attempts #

    # Get Attempt File Meta Data (List)
    @get("/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}")
    def fetch_attempt_file_metadata(self, response):
        return response

    # Get Attempt File Meta Data (List)
    @get("/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}/download")
    def download_attempt_file_metadata(self, response):
        return response

    # course grade notations #

    # Get Grade Notation(s)
    @get("/courses/{course_id}/gradebook/gradeNotations/{grade_notation_id}")
    def fetch_grade_notations(self, response):
        return response

    # course gradebook categories #

    # Get Gradebook Categori(es)
    @get("/courses/{course_id}/gradebook/categories/{category_id}")
    def fetch_gradebook_categories(self, response):
        return response

    # course grades #

    # Get Grade Schema(s)
    @get("/courses/{course_id}/gradebook/schemas/{schema_id}")
    def fetch_grade_schemas(self, response):
        return response

    # Get Grade Column(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}", 2)
    def fetch_grade_columns(self, response):
        return response

    # Get Grade Column Attempt(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}/attempts/{attempt_id}", 2)
    def fetch_column_attempts(self, response):
        return response

    # Get Column Grade(s)
    @get("/courses/{course_id}/gradebook/columns/{column_id}/users/{user_id}", 2)
    def fetch_column_grades(self, response):
        return response

    # Get Column Grades Last Changed
    @get("/courses/{course_id}/gradebook/columns/{column_id}/users/last_changed", 2)
    def fetch_column_grade_last_changed(self, response):
        return response

    # Get User Grades
    @get("/courses/{course_id}/gradebook/users/{user_id}", 2)
    def fetch_user_grades(self, response):
        return response

    # course grading periods #

    # Get Grading Period(s)
    @get("/courses/{course_id}/gradebook/periods/{period_id}")
    def fetch_grading_periods(self, response):
        return response

    # course group users #

    # Get Group Memberships
    @get("/courses/{course_id}/groups/{group_id}/users/{user_id}", 2)
    def fetch_group_memberships(self, response):
        return response

    # course groups #

    # Get Group(s)
    @get("/courses/{course_id}/groups/{group_id}", 2)
    def fetch_groups(self, response):
        return response

    # Get Group Set(s)
    @get("/courses/{course_id}/groups/sets/{group_id}", 2)
    def fetch_group_sets(self, response):
        return response

    # Get Group Set Children
    @get("/courses/{course_id}/groups/sets/{group_id}/groups", 2)
    def fetch_group_set_children(self, response):
        return response

    # course memberships #

    # Get Course Membership(s)
    @get("/courses/{course_id}/users/{user_id}")
    def fetch_course_memberships(self, response):
        return response

    # Get User Memberships
    @get("/users/{user_id}/courses")
    def fetch_user_memberships(self, response):
        return response

    # courses #

    # Get Course Child(ren)
    @get("/courses/{course_id}/children/{child_course_id}")
    def fetch_course_children(self, response):
        return response

    # Get Cross List Set
    @get("/courses/{course_id}/crossListSet")
    def fetch_cross_list_set(self, response):
        return response

    # Get Task
    @get("/courses/{course_id}/tasks/{task_id}")
    def fetch_task(self, response):
        return response

    # Get Course(s)
    @get("/courses/{course_id}", 3)
    def fetch_courses(self, response):
        return response

    # data sources #

    # Get Data Source(s)
    @get("/dataSources/{data_source_id}")
    def fetch_data_sources(self, response):
        return response

    # institutional hierarchy #

    # Get Associated Nodes
    @get("/courses/{course_id}/nodes")
    def fetch_associated_nodes(self, response):
        return response

    # Get Node(s)
    @get("/institutionalHierarchy/nodes/{node_id}")
    def fetch_nodes(self, response):
        return response

    # Get Node Children
    @get("/institutionalHierarchy/nodes/{node_id}/children")
    def fetch_node_children(self, response):
        return response

    # Get Node Course Associations
    @get("/institutionalHierarchy/nodes/{node_id}/courses")
    def fetch_node_course_associations(self, response):
        return response

    # lti #

    # Get Placement(s)
    @get("/lti/placements/{placement_id}")
    def fetch_placements(self, response):
        return response

    # Get Domain Config(s)
    @get("/lti/domains/{domain_id}")
    def fetch_domain_config(self, response):
        return response

    # performance dashboard #

    # Get Review Status By Course Id
    @get("/courses/{course_id}/performance/contentReviewStatus")
    def fetch_performance_review_status(self, response):
        return response

    # proctoring #

    # Get Proctoring Service(s)
    @get("/proctoring/services/{service_id}")
    def fetch_proctoring_services(self, response):
        return response

    # roles #

    # Get Course Role(s)
    @get("/courseRoles/{role_id}")
    def fetch_course_roles(self, response):
        return response

    # Get Institution Role(s)
    @get("/institutionRoles/{role_id}")
    def fetch_institution_roles(self, response):
        return response

    # Get System Role(s)
    @get("/systemRoles/{role_id}")
    def fetch_system_roles(self, response):
        return response

    # sessions #

    # Get Active Sessions
    @get("/sessions")
    def fetch_sessions(self, response):
        return response

    # SIS logs #

    # Get SIS Logs By Data Set Uid
    @get("/logs/sis/dataSets/{id}")
    def fetch_sis_logs(self, response):
        return response

    # system #

    # Get Policies
    @get("/system/policies/privacy")
    def fetch_policies(self, response):
        return response

    # Get System Task
    @get("/system/tasks/{task_id}")
    def fetch_system_task(self, response):
        return response

    # Get Version
    @get("/system/version")
    def fetch_version(self, response):
        return response

    # terms #

    # Get Term(s)
    @get("/terms/{term_id}")
    def fetch_terms(self, response):
        return response

    # uploads #

    # users #

    # Get Users(s)
    @get("/users/{user_id}")
    def fetch_users(self, response):
        return response

    # Get Users Avatar
    @get("/users/{user_id}/avatar")
    def fetch_avatar(self, response):
        return response

    # Get Observees
    @get("/users/{user_id}/observees")
    def fetch_observees(self, response):
        return response

    # Get Observers
    @get("/users/{user_id}/observers")
    def fetch_observers(self, response):
        return response

    # Get Current Active User By Id
    @get("/users/{user_id}/sessions")
    def fetch_current_active_user(self, response):
        return response


if __name__ == '__main__':
    pass
