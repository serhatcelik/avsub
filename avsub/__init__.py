# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub - A simplified command-line interface for FFmpeg."""

# pylint: disable=consider-using-f-string

from __future__ import absolute_import, print_function

import collections
import os
import platform
import sys

_OS = collections.namedtuple("_OS", ("nt", "posix"))
_NT_RELEASE = ("10", "11")
_PY_VERSION = (3, (6, 10))  # avsub: P3000

###############
# Requirement #
###############
_REQ_OS = _OS._fields

_REQ_NT_RELEASE = _NT_RELEASE
_REQ_NT = "%s-%s" % (_REQ_NT_RELEASE[0], _REQ_NT_RELEASE[-1])

_REQ_PY_MAJOR = _PY_VERSION[0]
_REQ_PY_MINOR = list(range(_PY_VERSION[1][0], _PY_VERSION[1][-1] + 1))
_REQ_PY = "%d.%d-%d" % (_REQ_PY_MAJOR, _REQ_PY_MINOR[0], _REQ_PY_MINOR[-1])

###########
# Current #
###########
_NOW_OS = os.name

_NOW_NT_RELEASE = platform.release()
_NOW_NT = _NOW_NT_RELEASE

_NOW_PY_MAJOR = sys.version_info[0]
_NOW_PY_MINOR = sys.version_info[1]
_NOW_PY = "%d.%d" % (_NOW_PY_MAJOR, _NOW_PY_MINOR)

if _NOW_PY_MAJOR != _REQ_PY_MAJOR or _NOW_PY_MINOR not in _REQ_PY_MINOR:
    print("[!] Expected Python %s, got Python %s instead" % (_REQ_PY, _NOW_PY))
    sys.exit(2)
if _NOW_OS not in _REQ_OS:
    print("[!] Unsupported operating system for AVsub:", _NOW_OS)
    sys.exit(2)

OS = _OS(*[name == os.name for name in _OS._fields])

# Do this check after Python check! (prevent false positive)
if OS.nt and _NOW_NT_RELEASE not in _REQ_NT_RELEASE:
    print("[!] Expected Win %s, got Win %s instead" % (_REQ_NT, _NOW_NT))
    sys.exit(2)
