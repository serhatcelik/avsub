# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This module provides ways to manipulate strings effectively."""

from __future__ import absolute_import

import hashlib
import os
import re
import stat
from typing import List

from avsub import OS
from avsub.core import errors
from avsub.core import x


class Str:
    """Base class for string manipulation."""

    def __init__(self, s: str) -> None:
        """Constructor method."""
        self._s: str = s

    def abs(self) -> str:
        """Normalize and absolutize the given string."""
        return os.path.abspath(self._s)

    def attrs(self) -> int:
        """Retrieve file attributes from the given string."""
        try:
            return os.stat(self.abs()).st_file_attributes
        except OSError as err:
            if errors.osraise(errors.ENOENT, err=err):
                raise
            return int(False)

    def base(self) -> str:
        """Return the basename of the given string."""
        return os.path.basename(self.abs())

    def endsext(self, ext: str) -> bool:
        """Check if the given string ends with the given extension."""
        return self._s.endswith("." + ext.strip("."))

    def exists(self) -> bool:
        """Check if the given string exists."""
        return os.path.exists(self.abs())

    def ext(self) -> str:
        """Retrieve file extension from the given string."""
        return os.path.splitext(self.base())[-1].strip(".")

    def extout(self) -> str:
        """Determine file extension from the given string."""
        return self.ext() if x.OPTS.ext == "-" else x.OPTS.ext

    def iscwd(self) -> bool:
        """Check if the given string is the working directory."""
        return self.abs() == Str(".").abs()

    def isdir(self) -> bool:
        """Check if the given string is an existing folder."""
        return os.path.isdir(self.abs())

    def isext(self) -> bool:
        """Check if the given string is a valid extension."""
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", self._s))  # avsub: C2011

    def isfile(self) -> bool:
        """Check if the given string is an existing file."""
        return os.path.isfile(self.abs())

    def isfull(self) -> bool:
        """Check if the given string, which is a folder, is full."""
        for _, folders, files in os.walk(self.abs()):
            return any([bool(folders), bool(files)])
        return False

    def ishidden(self) -> bool:
        """Check if the given string is hidden."""
        if OS.posix:
            return self.base().startswith(".")
        return bool(self.attrs() & stat.FILE_ATTRIBUTE_HIDDEN)

    def join(self, *args: str) -> str:
        """Join one or more string components intelligently."""
        return os.path.join(self.abs(), *[Str(_).base() for _ in args])

    def line(self, col: int = 0) -> str:
        """Create a horizontal line from the given string."""
        columns: int = col if col != 0 else os.get_terminal_size().columns - 1
        return self._s * columns

    def listdir(self) -> List[str]:
        """List the members of the given string, which is a folder."""
        return [Str(self._s).join(member) for member in os.listdir(self.abs())]

    def noext(self) -> str:
        """Remove file extension from the given string."""
        return os.path.splitext(self._s)[0]

    def sha256(self) -> str:
        """Calculate SHA256 hash of the giving string."""
        return hashlib.sha256(self._s.encode("utf-8")).hexdigest()
