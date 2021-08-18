# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import os
import re
import stat

from avsub.core import consts
from avsub.core import x


class Str:
    def __init__(self, s: str):
        self._s = s

    def abs(self) -> str:
        return os.path.abspath(self._s)  # Will be normalized and absolutized

    def attrs(self) -> int:
        try:
            return os.stat(self.abs()).st_file_attributes
        except (FileNotFoundError, PermissionError):
            return False

    def base(self) -> str:
        return os.path.basename(self.abs())

    def endsext(self, ext: str) -> bool:
        return self._s.endswith(".%s" % ext.strip("."))

    def exists(self) -> bool:
        return os.path.exists(self.abs())

    def ext(self) -> str:
        return os.path.splitext(self.base())[-1].strip(".")

    def extout(self) -> str:
        return self.ext() if x.OPTS.ext == "-" else x.OPTS.ext

    def iscwd(self) -> bool:
        return self.abs() == Str(".").abs()

    def isdir(self) -> bool:
        return os.path.isdir(self.abs())

    def isext(self) -> bool:
        return bool(re.search(r"^[a-zA-Z0-9_-]+$", self._s))  # avsub: C2011

    def isfile(self) -> bool:
        return os.path.isfile(self.abs())

    def isfull(self) -> bool:
        for _, folders, files in os.walk(self.abs()):
            return any([bool(folders), bool(files)])
        return False

    def ishidden(self) -> bool:
        if consts.POSIX:
            return self.base().startswith(".")
        return bool(self.attrs() & stat.FILE_ATTRIBUTE_HIDDEN)

    def join(self, *args: str) -> str:
        return os.path.join(self.abs(), *[Str(_).base() for _ in args])

    def noext(self) -> str:
        return os.path.splitext(self._s)[0]
