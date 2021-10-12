# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""Constants and utility functions for OSError exception."""

from __future__ import absolute_import

import errno

_EACCES: int = errno.EACCES  # Permission denied
_EINVAL: int = errno.EINVAL  # Invalid argument
_EPERM: int = errno.EPERM  # Operation not permitted
EEXIST: int = errno.EEXIST  # File exists
ENOENT: int = errno.ENOENT  # No such file or directory
ENOTDIR: int = errno.ENOTDIR  # Not a directory
ENOTEMPTY: int = errno.ENOTEMPTY  # Directory not empty


def osraise(*errnos: int, err: OSError) -> bool:
    """Determine whether to re-raise the given exception."""
    if err.errno in [*errnos, _EACCES, _EINVAL, _EPERM]:
        return False
    print(f"[Errno {err.errno}]")
    return True  # Will re-raise
