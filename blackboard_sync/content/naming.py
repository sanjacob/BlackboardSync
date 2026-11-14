"""
Build file and folder names that the local file system accepts
"""

from pathvalidate import sanitize_filename

# Most file systems limit a single file or folder name to 255 bytes
# (ext4, APFS) or 255 UTF-16 units (NTFS); 255 UTF-8 bytes fits both.
MAX_NAME_BYTES = 255


def safe_filename(name: str, suffix: str = "",
                  fallback: str = "Untitled") -> str:
    """Return `name` + `suffix` as a valid name for this platform.

    Characters this platform rejects are replaced with '_', and `name`
    is shortened so that the result, suffix included, fits within
    MAX_NAME_BYTES. The suffix (e.g. a file extension) is kept intact.
    """
    suffix = sanitize_filename(suffix, replacement_text="_",
                               platform="auto")
    max_len = MAX_NAME_BYTES - len(suffix.encode())
    stem = sanitize_filename(name, replacement_text="_",
                             platform="auto", max_len=max_len)
    return (stem or fallback) + suffix
