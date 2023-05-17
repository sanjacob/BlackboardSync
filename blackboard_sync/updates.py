"""
Checks for updates in GitHub.
"""

# Copyright (C) 2023, Jacob Sánchez Pérez

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

import requests
from typing import Optional
from packaging import version
from .__about__ import __version__


def check_for_updates() -> Optional[str]:
    """Checks if there is a newer release than the current on Github."""

    url = 'https://api.github.com/repos/jacobszpz/BlackboardSync/releases/latest'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        tag = json_response['tag_name']
        tag = tag[1:] if tag[0] == 'v' else tag
        if version.parse(tag) > version.parse(__version__):
            return json_response['html_url']

    return None


