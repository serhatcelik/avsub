# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""Module for Windows Registry manipulation."""

from __future__ import absolute_import

from winreg import CloseKey
from winreg import CreateKey
from winreg import HKEYType
from winreg import HKEY_CURRENT_USER
from winreg import QueryValueEx
from winreg import REG_SZ
from winreg import SetValueEx

from avsub.core import consts
from avsub.core import x


class Registry:
    """Base class for Windows Registry manipulation."""

    _open: HKEYType
    _v_name: str = "AVsub"

    def __init__(self) -> None:
        """Create and open the key."""
        self._open = CreateKey(HKEY_CURRENT_USER, consts.REG_KEY_RUN)

    def _v_exists(self) -> bool:
        """Check if the value already exists."""
        try:
            QueryValueEx(self._open, self._v_name)
        except FileNotFoundError:
            return False
        return True

    def set(self) -> None:
        """Set the value."""
        if not self._v_exists() or x.OPTS.fix_startup:
            SetValueEx(self._open, self._v_name, 0, REG_SZ, consts.REG_VAL_RUN)

    def __del__(self) -> None:
        """Close the key."""
        CloseKey(self._open)
