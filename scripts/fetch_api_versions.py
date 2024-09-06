"""
Ping all the Blackboard API servers listed in universities.json

This script is not meant to run on CI or automatically since some Blackboard
Learn servers may be temporarily down at any given time.
Instead this script may be run manually to test the `universities.json` file
and that all API URLs are correct.

You may invoke this script with the following command from the project root
`pytest scripts/fetch_api_versions.py -s`
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import sys
import requests
from enum import Enum, auto
import concurrent.futures
from json import JSONDecodeError

from blackboard_sync.institutions import _institutions

class APIResult(Enum):
    """Represents a specific outcome of an API request"""

    OK = auto()
    FAIL = auto()
    JSONERR = auto()
    CONNERR = auto()

    def __str__(self):
        color = lambda s: f"\033{s}\033[0m" 
        check, cross = color("[1;32m✓"), color("[91m✗")
        msg = {
            APIResult.OK: check,
            APIResult.FAIL: cross,
            APIResult.JSONERR: "[JSONDecodeError]",
            APIResult.CONNERR: "[ConnectionError]"
        }
        return msg[self]


def fetch_url(url, timeout):
    """Task that runs for every API url and attempts to fetch server version"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for non-2xx HTTP status codes
        data = response.json()
        if "learn" in data and "major" in data["learn"]:
            return APIResult.OK
        else:
            return APIResult.FAIL
    except requests.exceptions.ConnectionError:
        return APIResult.CONNERR
    except JSONDecodeError:
        return APIResult.JSONERR

def test_fetch_api_versions():
    """Ping many Blackboard API servers concurrently"""
    print("\n\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        v = lambda url: f"{url}/learn/api/public/v1/system/version"
        # Start the load operations and mark each future with its name
        future_to_uni = {executor.submit(fetch_url, v(uni.api_url), 20): uni.name for uni in _institutions}

        for future in concurrent.futures.as_completed(future_to_uni):
            uni_name = future_to_uni[future]
            try:
                result = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (uni_name, exc))
            else:
                print(f"{uni_name} {result}")


if __name__ == "__main__":
    raise SystemExit(test_fetch_api_versions())
