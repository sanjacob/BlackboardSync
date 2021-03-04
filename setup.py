#!/usr/bin/env python3

"""
Setup Script for BlackboardSync

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

from setuptools import setup
from blackboard_sync.__about__ import (__title__, __summary__, __uri__, __version__,
                                       __author__, __email__, __license__)

setup(name=__title__,
      version=__version__,
      description=__summary__,
      licence=__license__,
      author=__author__,
      author_email=__email__,
      url=__uri__,
      packages=['blackboard_sync'],
      install_requires=[
        "requests",
        "bs4",
        "lxml",
        "appdirs",
        "toml",
        "python-dateutil",
        "pyqt5<5.15.2"
        "setuptools"
      ],
      python_requires=">3.9")
