 #!/usr/bin/env python3

"""
BlackboardSync
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


from api import BlackboardSession

def main():
    username = ""
    password = ""
    user_id = "" 

    with open('secrets/login.txt') as login:
        username = login.readline().strip()
        password = login.readline().strip()
        user_id = login.readline().strip()

    u_sess = BlackboardSession(username, password)

    memberships = u_sess.fetchUserMemberships(user_id=user_id)

    for course in (membership for membership in memberships if membership['dataSourceId'] == '_21_1'):
        course_data = u_sess.fetchCourses(course_id=course['courseId'])

        code_split = course_data['name'].split(' : ')
        name_split = code_split[1].split(',')

        print(f"<{code_split[0]}> - <{name_split[0]}>")

        course_contents = u_sess.fetchContents(course_id=course['courseId'])

        for content_folder in course_contents:

            try:
                folder_children = u_sess.fetchContentChildren(course_id=course['courseId'],
                                                              content_id=content_folder['id'])

                print(f"    {content_folder['title']}")

                for child in folder_children:
                    type_tag = ""

                    if 'contentHandler' in child:
                        type = child['contentHandler']['id']

                        # if type == "resource/x-bb-document":
                        #     type_tag = "doc"
                        # elif type == "resource/x-bb-folder":
                        #     type_tag = "folder"
                        # elif type == "resource/x-bb-syllabus":
                        #     type_tag = "syllabus"
                        # elif type == "resource/x-bb-toollink":
                        #     type_tag = "toollink"

                        type_tag = f"[{type}]"

                    print(f"        {child['title']}{type_tag}")

            except ValueError:
                pass

        print()

if __name__ == '__main__':
    main()
