"""IP and RDAP utilities to enable university detection."""

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

import whoisit
import requests

IP_API = "https://api.ipify.org"
IP_TIMEOUT = 4


def find_my_ip() -> str | None:
    try:
        r = requests.get(IP_API, timeout=IP_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException:
        return None
    else:
        return r.text


def find_ip_entity(ip: str):
    try:
        whoisit.bootstrap()
        r = whoisit.ip(ip)
    except whoisit.errors.QueryError:
        return None
    except whoisit.errors.BootstrapError:
        return None
    else:
        return r
