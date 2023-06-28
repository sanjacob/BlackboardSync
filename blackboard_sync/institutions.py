"""Manages data of supported Blackboard partners."""

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

import json
import logging
from typing import Optional
from pathlib import Path

import requests
from pydantic import HttpUrl, BaseModel

__all__ = ['InstitutionLogin', 'InstitutionNetwork', 'Institution',
           'get_by_index', 'get_index_by_ip', 'get_names']


# logger = logging.getLogger(__name__)

# Local institution data fallback in case of no server
_local_data = 'universities.json'
# Frequently updated remote datafile
# _remote_data = 'https://example.com/universities.json'
# IP API
_ip_api_endpoint = 'http://ip-api.com/json?fields=org,isp'


class InstitutionLogin(BaseModel):
    """Elements of login flow for an `Institution`.

    :param `HttpUrl` start_url: Link to the Blackboard portal.
    :param `HttpUrl` target_url: Landing URL after login is complete.
    :param str username_input_selector: Selector for username input field.
    :param str password_input_selector: Selector for password input field.
    """

    start_url: HttpUrl
    target_url: HttpUrl


class InstitutionNetwork(BaseModel):
    """Possible network values for an `Institution`.

    :param list[str] org: Possible values for the organization field.
    :param list[str] isp: Possible values for the ISP field.
    """

    org: list[str]
    isp: list[str]


class Institution(BaseModel):
    """Institution with a Blackboard portal.

    :param str name: Long-format name of institution.
    :param str short_name: Most common abbreviation of name.
    :param list[str] data_sources: List of Blackboard data sources to download by default.
    :param `InstitutionLogin` login: Login metadata.
    :param `InstitutionNetwork` network: Network metadata.
    """

    name: str
    short_name: str
    data_sources: list[str]
    api_url: HttpUrl
    login: InstitutionLogin
    network: InstitutionNetwork


def load() -> list[Institution]:
    remote_found = False
    json_data = {}

    # try:
    #   json_data = requests.get(_remote_data).json()
    # except (requests.ConnectionError, json.decoder.JSONDecodeError):
    #   remote_found = False

    if not remote_found:
        with (Path(__file__).parent / _local_data).open() as f:
            json_data = json.load(f)

    return [Institution(**i) for i in json_data]


_institutions = load()


def get_by_index(i: int) -> Institution:
    """Retrieve institution at index specified.

    :param int i: Index of institution.
    """
    return _institutions[i]


def get_names() -> list[str]:
    """Get institution names."""
    return [f"{ins.name} ({ins.short_name})" for ins in _institutions]


def get_index_by_ip() -> Optional[int]:
    """Attempt to detect the user's institution by IP address data."""
    ip_info = {}

    try:
        ip_info = requests.get(_ip_api_endpoint).json()
    except (requests.ConnectionError, json.decoder.JSONDecodeError):
        pass

    ip_org = ip_info.get('org')
    ip_isp = ip_info.get('isp')

    for i, uni in enumerate(_institutions):
        found = False

        if ip_org:
            for org in uni.network.org:
                if ip_org == org:
                    found = True
        if ip_isp:
            for isp in uni.network.isp:
                if ip_isp == isp:
                    found = True
        if found:
            return i
    return None
