# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""Module for Windows Registry manipulation."""

from __future__ import absolute_import

import winreg as reg

from avsub.core import consts


class Registry:
    """Base class for Windows Registry manipulation."""

    _open: reg.HKEYType

    def __init__(self):
        """Create and open the key."""
        self._open = reg.CreateKey(reg.HKEY_CURRENT_USER, consts.REG_KEY_RUN)

    def set(self):
        """Set the value."""
        reg.SetValueEx(self._open, "AVsub", 0, reg.REG_SZ, consts.REG_VAL_RUN)

    def __del__(self):
        """Close the key."""
        reg.CloseKey(self._open)
