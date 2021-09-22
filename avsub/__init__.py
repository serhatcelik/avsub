# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
AVsub - A simplified command-line interface for FFmpeg.
"""

import os
import sys

NT = "nt"
POSIX = "posix"
_ALL_OPERATING_SYSTEMS = [NT, POSIX]
OS = {_: os.name == _ for _ in _ALL_OPERATING_SYSTEMS}

_MAJOR = 3
_MINOR_MIN = 6  # avsub: P2000
_MINOR_MAX = 9

###############
# Requirement #
###############
_OS_REQ = OS
_MAJOR_REQ = _MAJOR
_MINOR_REQ = range(_MINOR_MIN, _MINOR_MAX + 1)
_PYTHON_REQ = "%d.%d-%d" % (_MAJOR, _MINOR_MIN, _MINOR_MAX)

###########
# Current #
###########
_OS_NOW = os.name
_MAJOR_NOW = sys.version_info[0]
_MINOR_NOW = sys.version_info[1]
_PYTHON_NOW = "%d.%d" % (_MAJOR_NOW, _MINOR_NOW)

if _OS_NOW not in _OS_REQ:  # avsub: N2203
    print("[!] Unsupported operating system for AVsub:", _OS_NOW)
    sys.exit(2)
if _MAJOR_NOW != _MAJOR_REQ or _MINOR_NOW not in _MINOR_REQ:
    print("[!] Expected Python %s, got Python %s" % (_PYTHON_REQ, _PYTHON_NOW))
    sys.exit(2)
