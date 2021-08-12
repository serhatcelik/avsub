# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import ctypes
import os
import stat

from avsub.core import x
from avsub.str import Str


def get_files(parent: str) -> list:
    try:
        files = [Str(parent).join(_) for _ in os.listdir(Str(parent).abs())]
    except (FileNotFoundError, NotADirectoryError, PermissionError) as err:
        print(err)
        return []

    hidden = x.OPTS.hidden
    exclude = set(x.OPTS.exclude)
    only = set(x.OPTS.oext)

    for member in files.copy():
        if any([
            Str(member).isdir(),
            all([not bool(hidden), Str(member).ishidden()]),
            all([bool(exclude), any(Str(member).endsext(_) for _ in exclude)]),
            all([bool(only), not any(Str(member).endsext(_) for _ in only)]),
        ]):
            files.remove(member)

    return files


def create_output(parent: str, file: str) -> str:
    basename_no_ext = os.path.splitext(Str(file).base())[0]
    return Str(parent).join(".".join([basename_no_ext, Str(file).ext()]))


def mark_as_not_processed(parent: str, files: list) -> None:
    for file in files:
        output = create_output(parent=parent, file=file)
        x.NOT_PROCESSED.update({file: output})


def mark_as_hidden(file: str) -> None:
    current = Str(file).attrs()
    changed = current | stat.FILE_ATTRIBUTE_HIDDEN
    ctypes.windll.kernel32.SetFileAttributesW(Str(file).abs(), changed)


def cleaner(*args: dict) -> None:
    for container in args:
        for output in container.values():
            try:
                os.remove(output)
            except (FileNotFoundError, PermissionError):
                continue
            except OSError as err:
                # 22: Invalid argument
                if err.errno == 22:
                    pass
                else:
                    raise
