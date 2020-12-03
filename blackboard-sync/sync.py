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
import logging
from pathlib import Path
from getpass import getpass
from api import BlackboardSession
from blackboard import BBCourse, BBMembership, BBContentHandler, BBCourseContent, BBContentChild
from appdirs import user_config_dir


class BlackboardSync:
    _config_filename = "blackboard_sync"
    persistance = True
    user_id = ""
    data_source = "_21_1"

    def __init__(self):
        self.config_folder = Path(user_config_dir(appauthor="WeAreMagic",
                                                  roaming=True))

        self.config_file = self.config_folder / self._config_filename

        if self.config_file.exists():
            self.loadConfig()
        else:
            self.configure()

        self.sync_folder = Path('sync')

        if not self.sync_folder.exists():
            self.sync_folder.mkdir()

        self.main()

    def loadConfig(self):
        with open(self.config_file) as config_file:
            config = toml.load(config_file)
            login = config['Login']
            sync = config['Sync']

        try:
            u_sess = BlackboardSession(login['username'], login['password'])
            u_sess.logger.addHandler(logging.StreamHandler())
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


    def handle_file(self, content, parent_path, course_id, depth=0):
        print(f"{'    ' * depth}{content.title}[{content.contentHandler.id}]")

        type = content.contentHandler
        file_path = Path(parent_path / content.title_nb)

        if type.isFolder:
            try:
                children = self.sess.fetchContentChildren(course_id=course_id,
                                                          content_id=content.id)

                if children:
                    file_path.mkdir(exist_ok=True, parents=True)

                for child in children:
                    self.handle_file(BBContentChild(**child), file_path, course_id, depth + 1)
            except ValueError:
                pass
        elif type.isDocument and content.body:
            with file_path.with_name(f"{file_path.name}.md").open('w') as md:
                md.write(content.body)


    def main(self):
        all_memberships = self.sess.fetchUserMemberships(user_id=self.user_id)
        filtered_ms = []

        for membership in all_memberships:
            new_ms = BBMembership(**membership)
            if new_ms.dataSourceId == self.data_source:
                filtered_ms.append(new_ms)

        for ms in filtered_ms:
            course = BBCourse(**self.sess.fetchCourses(course_id=ms.courseId))
            code_split = course.name.split(' : ')
            name_split = code_split[1].split(',')

            print(f"<{code_split[0]}> - <{name_split[0]}>")

            course_contents = self.sess.fetchContents(course_id=course.id)

            if course_contents:
                course_path = Path(self.sync_folder / ms.created[:4] / name_split[0])

            for content in (BBCourseContent(**content) for content in course_contents):
                self.handle_file(content, course_path, course.id, 1)

            print()


if __name__ == '__main__':
    bb_sync = BlackboardSync()
