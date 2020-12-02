 #!/usr/bin/env python3

"""
BlackboardSync,
a utility to download files and metadata
from Blackboard

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

import toml
from pathlib import Path
from getpass import getpass
from api import BlackboardSession
from appdirs import user_config_dir


class BlackboardSync:
    _config_filename = "blackboard_sync"
    persistance = True
    user_id = ""

    def __init__(self):
        self.config_folder = Path(user_config_dir(appauthor="WeAreMagic",
                                                  roaming=True))

        self.config_file = self.config_folder / self._config_filename

        if self.config_file.exists():
            self.loadConfig()
        else:
            self.configure()

        self.main()

    def loadConfig(self):
        with open(self.config_file) as config_file:
            config = toml.load(config_file)
            login = config['Login']
            sync = config['Sync']

        try:
            u_sess = BlackboardSession(login['username'], login['password'])
        except ValueError:
            print("Saved credentials are incorrect, launching configure")
            self.configure()
        else:
            self.sess = u_sess
            self.user_id = sync['user_id']

    def saveConfig(self, username, password, user_id):
        with open(self.config_file, 'w') as config_out:
            config_dict = {'Login': {'username': username,
                                     'password': password},
                           'Sync': {'user_id': user_id}}

            toml.dump(config_dict, config_out)

    def configure(self):
        authorized = False

        print("This is the BlackboardSync configuration script")
        print("You should only need to run this once, your parameters will be saved")
        print()
        print("You will need to know your Blackboard user id")
        print("Currently there's no known easy way to obtain it")
        print("Try playing around with the Blackboard API")
        print("https://developer.blackboard.com/portal/displayApi")
        print("Alternatively, send me an email with your full name")
        print()

        while not authorized:
            print()
            username = input("Enter your UCLan mail: ")
            password = getpass("Enter your password: ")
            user_id = input("Enter your user id: ")

            placeholder_pass = '*' * len(password)

            save = input(f"Use login configuration {username}: {placeholder_pass}? [Y/n]")

            if save.lower() != "n":
                try:
                    u_sess = BlackboardSession(username, password)
                except ValueError:
                    print("Login parameters are incorrect, try again")
                else:
                    if self.persistance:
                        self.saveConfig(username, password, user_id)

                    self.sess = u_sess
                    self.user_id = user_id
                    authorized = True

    def main(self):
        memberships = self.sess.fetchUserMemberships(user_id=self.user_id)

        for course in (membership for membership in memberships if membership['dataSourceId'] == '_21_1'):
            course_data = self.sess.fetchCourses(course_id=course['courseId'])

            code_split = course_data['name'].split(' : ')
            name_split = code_split[1].split(',')

            print(f"<{code_split[0]}> - <{name_split[0]}>")

            course_contents = self.sess.fetchContents(course_id=course['courseId'])

            for content_folder in course_contents:

                try:
                    folder_children = self.sess.fetchContentChildren(course_id=course['courseId'],
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
    bb_sync = BlackboardSync()
