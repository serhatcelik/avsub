# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub - A simplified command-line interface for FFmpeg."""

import sys

MAJOR_REQ = 3
MINOR_MIN = 5
MINOR_MAX = 9

major = sys.version_info[0]
minor = sys.version_info[1]

if not (major == MAJOR_REQ and (minor in range(MINOR_MIN, MINOR_MAX + 1))):
    sys.exit("[!] Requires Python ~=%d.%d, not %d.%d" % (MAJOR_REQ, MINOR_MIN,
                                                         major, minor))
