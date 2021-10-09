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
import sys

_Os = collections.namedtuple("_Os", ("nt", "posix"))
_MAJOR = 3
_MINOR_MIN = 6
_MINOR_MAX = 10  # avsub: P3000

###############
# Requirement #
###############
_OS_REQ = _Os._fields
_MAJOR_REQ = _MAJOR
_MINOR_REQ = list(range(_MINOR_MIN, _MINOR_MAX + 1))
_PYTHON_REQ = "%d.%d-%d" % (_MAJOR_REQ, _MINOR_REQ[0], _MINOR_REQ[-1])

###########
# Current #
###########
_OS_NOW = os.name
_MAJOR_NOW = sys.version_info[0]
_MINOR_NOW = sys.version_info[1]
_PYTHON_NOW = "%d.%d" % (_MAJOR_NOW, _MINOR_NOW)

if _OS_NOW not in _OS_REQ:
    print("[!] Unsupported operating system for AVsub:", _OS_NOW)
    sys.exit(2)
if _MAJOR_NOW != _MAJOR_REQ or _MINOR_NOW not in _MINOR_REQ:
    print("[!] Expected Python %s, got Python %s" % (_PYTHON_REQ, _PYTHON_NOW))
    sys.exit(2)

OS = _Os(*[_ == os.name for _ in _Os._fields])
