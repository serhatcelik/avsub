# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import ctypes
import os
import re
import stat
import sys
import time
from subprocess import CalledProcessError, DEVNULL as NULL, TimeoutExpired
from subprocess import check_call, run
from typing import Dict, List, Set, Union

from avsub import NT, OS, POSIX
from avsub.core import consts, errors, x
from avsub.str import Str


class Repeater:
    def __init__(self, retry: int, countdown: int):
        self.retry: int = retry
        self.countdown: int = countdown
        self.i: int = 0

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except consts.EXCEPTION_BY_FUNCTION[self.f_name(func)] as err:
                if self.i == self.retry:
                    return False

                print("[!]", err)
                print(self.r_message())

                start: float = time.monotonic()
                while time.monotonic() - start < self.countdown:
                    continue

                self.i += 1

                return wrapper(*args, **kwargs)

        return wrapper

    def r_message(self) -> str:
        pbar: str = "[%*d/%d]" % (len(str(self.retry)), self.i + 1, self.retry)
        return "[*] Retrying %s in %d seconds..." % (pbar, self.countdown)

    @staticmethod
    def f_name(func) -> str:
        return ".".join([func.__module__, func.__name__])


def avsubprocess(cmd: List[str], call: bool = False, timeout: int = 5) -> None:
    if call:
        check_call(cmd, timeout=timeout, stdin=NULL, stdout=NULL, stderr=NULL)
    else:
        run(cmd, check=True, stdin=NULL)


def convert_trim() -> Union[str, List[int]]:  # avsub: N2201
    if all(_.isdigit() for _ in x.OPTS.trim):
        first: int = int(x.OPTS.trim[0])
        last: int = int(x.OPTS.trim[1])
        return "smaller" if last <= first else [first, last]

    if all(bool(re.match(r"^\d+:[0-5]?\d:[0-5]?\d$", _)) for _ in x.OPTS.trim):
        hour_f: int = int(x.OPTS.trim[0].split(":")[0])
        min_f: int = int(x.OPTS.trim[0].split(":")[1])
        sec_f: int = int(x.OPTS.trim[0].split(":")[2])
        hour_l: int = int(x.OPTS.trim[1].split(":")[0])
        min_l: int = int(x.OPTS.trim[1].split(":")[1])
        sec_l: int = int(x.OPTS.trim[1].split(":")[2])
        secs_f: int = hour_f * 3600 + min_f * 60 + sec_f
        secs_l: int = hour_l * 3600 + min_l * 60 + sec_l
        return "smaller" if secs_l <= secs_f else [secs_f, secs_l]

    return "syntax"  # Error type


def create_output(parent: str, file: str) -> str:
    basename_no_ext: str = Str(Str(file).base()).noext()
    return Str(parent).join(".".join([basename_no_ext, Str(file).extout()]))


def dcleaner(*args: List[str]) -> None:  # avsub: N2204
    for container in args:
        for folder in container:
            try:
                if folder is not None:
                    os.rmdir(Str(folder).abs())
            except OSError as err:
                if errors.osraise(errors.ENOENT, errors.ENOTEMPTY, err=err):
                    raise
                continue


def dopen(folder: str) -> None:
    if folder is not None and Str(folder).isdir():
        if any([
            x.OPTS.no_open_dir == "never",
            x.OPTS.no_open_dir == "empty" and Str(folder).isfull(),
        ]):
            if OS[NT]:
                os.startfile(Str(folder).abs(), "open")  # pylint: disable=E1101
            else:  # avsub: C2005
                try:
                    avsubprocess(["xdg-open", Str(folder).abs()], call=True)
                except (FileNotFoundError, CalledProcessError, TimeoutExpired):
                    pass


def fcleaner(*args: Dict[str, str]) -> None:
    for container in args:
        for output in container.values():
            try:
                os.remove(Str(output).abs())
            except OSError as err:
                if errors.osraise(errors.ENOENT, err=err):
                    raise
                continue


def get_files(parent: str) -> Union[list, List[str]]:
    try:
        files: List[str] = Str(parent).listdir()
    except OSError as err:
        if errors.osraise(errors.ENOENT, errors.ENOTDIR, err=err):
            raise
        print(err)
        return []

    hidden: bool = x.OPTS.hidden
    exclude: Set[str] = set(x.OPTS.exclude)
    only: Set[str] = set(x.OPTS.only)

    for member in files.copy():
        if any([
            Str(member).isdir(),
            all([not hidden, Str(member).ishidden()]),
            all([bool(exclude), any(Str(member).endsext(_) for _ in exclude)]),
            all([bool(only), not any(Str(member).endsext(_) for _ in only)]),
        ]):
            files.remove(member)

    return files


def is_a_foreground() -> bool:
    if OS[POSIX]:
        return os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno())  # pylint: disable=E1101
    return True


def is_a_tty() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()


def is_user_admin() -> bool:
    if OS[POSIX]:
        return os.geteuid() == 0  # pylint: disable=E1101
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def mark_as_hidden(file: str) -> None:
    current: int = Str(file).attrs()
    changed: int = current | stat.FILE_ATTRIBUTE_HIDDEN
    ctypes.windll.kernel32.SetFileAttributesW(Str(file).abs(), changed)


def mark_as_not_processed(parent: str, files: List[str]) -> None:
    for file in files:
        x.NOT_PROCESSED.update({file: create_output(parent=parent, file=file)})
