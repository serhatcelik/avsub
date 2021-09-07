# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import errno

_EACCES: int = errno.EACCES  # Permission denied
_EINVAL: int = errno.EINVAL  # Invalid argument
_EPERM: int = errno.EPERM  # Operation not permitted
ENOENT: int = errno.ENOENT  # No such file or directory
ENOTDIR: int = errno.ENOTDIR  # Not a directory
ENOTEMPTY: int = errno.ENOTEMPTY  # Directory not empty


def osraise(*args: int, err: OSError) -> bool:
    if err.errno in [*args, _EACCES, _EINVAL, _EPERM]:
        return False
    return True  # Will raise
