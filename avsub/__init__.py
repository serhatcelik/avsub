# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub : A simplified CLI for FFmpeg."""

import sys

if True in [
    sys.version_info.major != 3,
    sys.version_info.major == 3 and sys.version_info.minor < 5,
]:
    sys.exit("F : Requires Python ~=3.5")
