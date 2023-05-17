"""
University

Manage the university information.
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

import json
from typing import List, Any
from pathlib import Path
from pydantic import BaseModel


class LoginInfo(BaseModel):
    start_url: str
    target_url: str


class NetworkInfo(BaseModel):
    isp: List[str] = []
    org: List[str] = []


class UniversityInfo(BaseModel):
    name: str
    short_name: str
    login: LoginInfo
    api_url: str
    network: NetworkInfo = None
    data_sources: List[str] = []


class UniversityDB:
    db = Path(__file__).resolve().parent / 'universities.json'

    @classmethod
    def all(cls) -> List[Any]:
        with cls.db.open('r') as file:
            return [u.get('name') for u in json.load(file)]

    @classmethod
    def get(cls, university_index: int):
        # Get the path of the DB

        with cls.db.open('r') as file:
            data = json.load(file)

            if len(data) > university_index:
                university_data = data[university_index]
                university = UniversityInfo(**university_data)
                return university
