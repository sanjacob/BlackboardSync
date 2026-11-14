"""
Build file and folder names that the local file system accepts
"""

# Copyright (C) 2026, Jacob Sánchez Pérez

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


from pathvalidate import sanitize_filename

# Most file systems limit a single file or folder name to 255 bytes
# (ext4, APFS) or 255 UTF-16 units (NTFS); 255 UTF-8 bytes fits both.
MAX_NAME_BYTES = 255


def safe_filename(name: str, suffix: str = "",
                  fallback: str = "Untitled") -> str:
    """Return `name` + `suffix` as a name valid on every platform.

    Characters that any supported platform rejects (e.g. `/` on all of
    them, `:` or `?` on Windows) are replaced with '_', so a course syncs
    to the same names on Windows, macOS and Linux. `name` is shortened
    so that the result, suffix included, fits within MAX_NAME_BYTES.
    The suffix (e.g. a file extension) is kept intact.
    """
    suffix = sanitize_filename(suffix, replacement_text="_",
                               platform="universal")
    max_len = MAX_NAME_BYTES - len(suffix.encode())
    stem = sanitize_filename(name, replacement_text="_",
                             platform="universal", max_len=max_len)
    return (stem or fallback) + suffix
