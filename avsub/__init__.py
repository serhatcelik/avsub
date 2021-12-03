# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub — A simplified command-line interface for FFmpeg."""

# pylint: disable=consider-using-f-string

from __future__ import absolute_import
from __future__ import print_function

import collections
import os
import platform
import sys

_OS = collections.namedtuple("_OS", ("nt", "posix"))
_MIN_NT = 10
_MIN_PY = (3, 6)

###############
# Requirement #
###############
_REQ_OS = _OS._fields

_REQ_NT_RELEASE = _MIN_NT
_REQ_NT = "%d+" % _REQ_NT_RELEASE

_REQ_PY_MAJOR = _MIN_PY[0]
_REQ_PY_MINOR = _MIN_PY[1]
_REQ_PY = "%d.%d+" % (_REQ_PY_MAJOR, _REQ_PY_MINOR)

###########
# Current #
###########
_NOW_OS = os.name

_NOW_PY_MAJOR = sys.version_info[0]
_NOW_PY_MINOR = sys.version_info[1]
_NOW_PY = "%d.%d" % (_NOW_PY_MAJOR, _NOW_PY_MINOR)

if _NOW_PY_MAJOR != _REQ_PY_MAJOR or _NOW_PY_MINOR < _REQ_PY_MINOR:
    print("[!] Expected Python %s, got Python %s instead" % (_REQ_PY, _NOW_PY))
    sys.exit(2)
if _NOW_OS not in _REQ_OS:  # avsub: N2203
    print("[!] Unsupported operating system for AVsub:", _NOW_OS)
    sys.exit(2)

OS = _OS(*[name == _NOW_OS for name in _OS._fields])

# Do this check after Python check! (prevent false-positive)
if OS.nt:
    _NOW_NT_RELEASE = platform.release()
    _NOW_NT = _NOW_NT_RELEASE

    if not _NOW_NT_RELEASE.isdigit():  # avsub: C2400
        print("[!] Unknown Windows release:", _NOW_NT_RELEASE)
        sys.exit(2)
    if int(_NOW_NT_RELEASE) < _REQ_NT_RELEASE:
        print("[!] Expected Win %s, got Win %s instead" % (_REQ_NT, _NOW_NT))
        sys.exit(2)
