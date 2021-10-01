# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This module provides ways to manipulate strings effectively."""

from __future__ import absolute_import

import os
import re
import stat
from typing import List, Union

from avsub import OS
from avsub.core import errors, x


class Str:
    """Docstring."""

    def __init__(self, s: str) -> None:
        """Docstring."""
        self._s: str = s

    def abs(self) -> str:
        """Docstring."""
        return os.path.abspath(self._s)  # Will be normalized and absolutized

    def attrs(self) -> Union[bool, int]:
        """Docstring."""
        try:
            return os.stat(self.abs()).st_file_attributes
        except OSError as err:
            if errors.osraise(errors.ENOENT, err=err):
                raise
            return False

    def base(self) -> str:
        """Docstring."""
        return os.path.basename(self.abs())

    def endsext(self, ext: str) -> bool:
        """Docstring."""
        return self._s.endswith("." + ext.strip("."))

    def exists(self) -> bool:
        """Docstring."""
        return os.path.exists(self.abs())

    def ext(self) -> str:
        """Docstring."""
        return os.path.splitext(self.base())[-1].strip(".")

    def extout(self) -> str:
        """Docstring."""
        return self.ext() if x.OPTS.ext == "-" else x.OPTS.ext

    def iscwd(self) -> bool:
        """Docstring."""
        return self.abs() == Str(".").abs()

    def isdir(self) -> bool:
        """Docstring."""
        return os.path.isdir(self.abs())

    def isext(self) -> bool:
        """Docstring."""
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", self._s))  # avsub: C2011

    def isfile(self) -> bool:
        """Docstring."""
        return os.path.isfile(self.abs())

    def isfull(self) -> bool:
        """Docstring."""
        for _, folders, files in os.walk(self.abs()):
            return any([bool(folders), bool(files)])
        return False

    def ishidden(self) -> bool:
        """Docstring."""
        if OS.posix:
            return self.base().startswith(".")
        return bool(self.attrs() & stat.FILE_ATTRIBUTE_HIDDEN)

    def issafe(self, char: str = " ") -> bool:
        """Docstring."""
        return char not in self.base()

    def join(self, *args: str) -> str:
        """Docstring."""
        return os.path.join(self.abs(), *[Str(_).base() for _ in args])

    def line(self, col: int = 0) -> str:
        """Docstring."""
        columns: int = col if col != 0 else os.get_terminal_size().columns - 1
        return self._s * columns

    def listdir(self) -> List[str]:
        """Docstring."""
        return [Str(self._s).join(_) for _ in os.listdir(self.abs())]

    def noext(self) -> str:
        """Docstring."""
        return os.path.splitext(self._s)[0]
