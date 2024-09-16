"""Loads and provides data about supported universities."""

# Copyright (C) 2024, Jacob Sánchez Pérez

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import json
import logging
from pathlib import Path

from pydantic import HttpUrl, BaseModel

from .ip import find_my_ip, find_ip_entity


__all__ = [
    'InstitutionLogin',
    'InstitutionNetwork',
    'InstitutionContent',
    'Institution',
    'get_names',
    'get_by_index',
    'autodetect'
]


logger = logging.getLogger(__name__)

UNIVERSITY_DB = 'universities.json'


class InstitutionLogin(BaseModel):
    start_url: HttpUrl
    target_url: HttpUrl


class InstitutionNetwork(BaseModel):
    name: list[str] = []


class InstitutionContent(BaseModel):
    data_sources: list[str] = []


class Institution(BaseModel):
    """A university/college with a Blackboard Learn instance."""

    name: str
    """Official university name."""

    short_name: str | None = None
    """Abbreviation used to facilitate search."""

    country: str | None = None
    """Country of university."""

    api_url: HttpUrl
    """URL of the Blackboard Learn REST API instance."""

    login: InstitutionLogin
    """Metadata to make login possible."""

    network: InstitutionNetwork | None = None
    """Metadata to enable automatic detection."""

    content: InstitutionContent | None = None
    """Metadata to improve content filtering."""


def load() -> list[Institution]:
    db = []

    with (Path(__file__).parent / UNIVERSITY_DB).open() as f:
        db = json.load(f)

    return [Institution(**uni) for uni in db]


_institutions = load()


def get_by_index(i: int) -> Institution:
    """Get the institution with the given id."""
    return _institutions[i]


def get_names() -> list[str]:
    """Get university names for search."""
    names = []

    for uni in _institutions:
        tag = f"{uni.name} ({uni.short_name})" if uni.short_name else uni.name
        names.append(tag)
    return names


def autodetect() -> int | None:
    """Detect university based on ISP information."""

    my_ip = find_my_ip()

    if my_ip is None:
        return None

    entity = find_ip_entity(my_ip)

    if entity is None:
        return None

    name = entity['name']
    description = entity['description']

    for i, uni in enumerate(_institutions):
        # First heuristic, network description
        # Works only with full university name
        if description and description[0] == uni.name:
            return i

        # Second heuristic, network name
        # More specific but must be specified manually
        if uni.network and any(name == x for x in uni.network.name):
            return i
    return None
