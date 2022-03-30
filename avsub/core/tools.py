# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""General utility classes and functions."""

from __future__ import absolute_import

import ctypes
import os
import re
import signal
import stat
import sys
import threading
import time
from datetime import datetime
from datetime import timedelta
from subprocess import CalledProcessError  # nosec
from subprocess import DEVNULL as NULL  # nosec
from subprocess import TimeoutExpired  # nosec
from subprocess import check_call  # nosec
from subprocess import run  # nosec
from typing import Dict, List, Set, Union

from avsub import OS
from avsub.core import consts
from avsub.core import errors
from avsub.core import x
from avsub.core.consts import U8, XML
from avsub.str import Str


def repeater(retry: int, countdown: float):
    """Repetitive task handler."""
    def decorator(func):
        """Decorator function."""
        def wrapper(*args, **kwargs):
            """Wrapper function."""
            f_name: str = ".".join([func.__module__, func.__name__])
            for i in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except consts.EXCEPTION_BY_FUNCTION[f_name] as err:
                    print("[!]", err)  # avsub: F2221
                    if i == retry:
                        break
                    pbar: str = create_progress(i, total=retry)
                    print(f"[*] Retrying {pbar} in {countdown} secs...")
                    time.sleep(countdown)
            return False
        return wrapper
    return decorator


class SigHandler:
    """Signal handler."""

    _handler = None

    def __init__(self, signals: Dict[str, int]) -> None:
        """Constructor method."""
        self._signals: Dict[str, int] = signals

    def _handle(self) -> None:
        for sig in self._signals.values():
            if threading.current_thread() is threading.main_thread():
                signal.signal(sig, self._handler)

    def capture(self, func) -> None:
        """Enable signal capture."""
        self._handler = func
        self._handle()

    def ignore(self) -> None:
        """Disable signal capture."""
        self._handler = signal.SIG_IGN
        self._handle()


def avsubprocess(cmd: List[str], call: bool = False, timeout: int = 5) -> None:
    """A custom subprocess for AVsub."""
    if call:
        check_call(cmd, timeout=timeout, stdin=NULL, stdout=NULL, stderr=NULL)
    else:
        run(cmd, check=True, stdin=NULL)


def clear_cache() -> str:
    """Clear cache information."""
    if "--clear-cache" in sys.argv:
        fcleaner({consts.FILE_CACHE: consts.FILE_CACHE})
        return "[+] Cache cleared"
    return ""


def convert_trim() -> Union[str, List[str]]:  # avsub: N2201
    """Check the syntax of the trim command."""
    if all(_.isdigit() for _ in x.OPTS.trim):
        first: int = int(x.OPTS.trim[0])
        last: int = int(x.OPTS.trim[1])
        return "smaller" if last <= first else [str(first), str(last)]

    if all(bool(re.match(r"^\d+:[0-5]?\d:[0-5]?\d$", _)) for _ in x.OPTS.trim):
        hour_f: int = int(x.OPTS.trim[0].split(":")[0])
        min_f: int = int(x.OPTS.trim[0].split(":")[1])
        sec_f: int = int(x.OPTS.trim[0].split(":")[2])
        hour_l: int = int(x.OPTS.trim[1].split(":")[0])
        min_l: int = int(x.OPTS.trim[1].split(":")[1])
        sec_l: int = int(x.OPTS.trim[1].split(":")[2])
        secs_f: int = hour_f * 3600 + min_f * 60 + sec_f
        secs_l: int = hour_l * 3600 + min_l * 60 + sec_l
        return "smaller" if secs_l <= secs_f else [str(secs_f), str(secs_l)]

    return "syntax"  # Error type


def create_output(parent: str, file: str) -> str:
    """Create an output from input for the ultimate FFmpeg command."""
    basename_no_ext: str = Str(Str(file).base()).noext()
    return Str(parent).join(".".join([basename_no_ext, Str(file).extout()]))


def create_progress(current: int, total: Union[int, list]) -> str:
    """Create a fake progress bar."""
    if isinstance(total, int):
        return f"[{(current + 1):>{len(str(total))}}/{total}]"
    return f"[{(current + 1):>{len(str(len(total)))}}/{len(total)}]"


def create_startup_program() -> bool:
    """Create a startup program to auto check for updates."""
    if Str(consts.FILE_STARTUP).isfile() and not x.OPTS.fix_startup:
        return True
    try:
        with open(consts.FILE_STARTUP, "w", encoding=U8) as bat:
            bat.write("avsub\n"
                      "pause\n")
    except OSError as err:
        if errors.osraise(errors.ENOENT, err=err):
            raise
        return False
    return True


def dcleaner(*containers: List[str]) -> None:  # avsub: N2204
    """Delete folders that to be deleted on exit."""
    for container in containers:
        for folder in container:
            try:
                if folder is not None:
                    os.rmdir(Str(folder).abs())
            except OSError as err:
                if errors.osraise(errors.ENOENT, errors.ENOTEMPTY, err=err):
                    raise
                continue


def dmaker(*folders: str, exist_ok: bool = True) -> None:
    """Make folders."""
    for folder in folders:
        os.makedirs(folder, exist_ok=exist_ok)


def dopen(folder: str) -> None:
    """Open a folder."""
    if all([not x.OPTS.shut, folder is not None, Str(folder).isdir()]):
        if any([
            x.OPTS.no_open_dir == "never",
            x.OPTS.no_open_dir == "empty" and Str(folder).isfull(),
        ]):
            if hasattr(os, "startfile"):
                getattr(os, "startfile")(Str(folder).abs())
            else:  # avsub: C2005
                try:
                    avsubprocess(["xdg-open", Str(folder).abs()], call=True)
                except (FileNotFoundError, CalledProcessError, TimeoutExpired):
                    pass


def fcleaner(*containers: Dict[str, str]) -> None:
    """Delete files that to be deleted on exit."""
    for container in containers:
        for output in container.values():
            try:
                os.remove(Str(output).abs())
            except OSError as err:
                if errors.osraise(errors.ENOENT, err=err):
                    raise
                continue


def get_files(parent: str) -> Union[list, List[str]]:
    """Get the members of the given folder."""
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
    done: Set[str] = set(get_files_from_cache())
    use: bool = x.OPTS.use_cache

    for member in files.copy():
        if any([
            Str(member).isdir(),
            all([not hidden, Str(member).ishidden()]),
            all([bool(exclude), any(Str(member).endsext(_) for _ in exclude)]),
            all([bool(only), not any(Str(member).endsext(_) for _ in only)]),
            all([use, Str(member).sha256() in done]),
        ]):
            files.remove(member)

    return files


def get_files_from_cache() -> Union[list, List[str]]:
    """Get hashes from the cache."""
    try:
        with open(consts.FILE_CACHE, "r", encoding=U8) as cache:
            return [hash_.strip() for hash_ in cache.readlines()]
    except OSError as err:
        if errors.osraise(errors.ENOENT, err=err):
            raise
        return []


def is_a_foreground() -> bool:
    """Check if a process is running in the foreground."""
    if hasattr(os, "getpgrp") and hasattr(os, "tcgetpgrp"):
        fd_: int = sys.stdout.fileno()
        return getattr(os, "getpgrp")() == getattr(os, "tcgetpgrp")(fd_)
    return True


def is_a_tty() -> bool:
    """Check if all file objects are attached to a tty(-like) device."""
    return sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()


def is_user_an_admin() -> bool:
    """Check if the current user is an administrator."""
    if hasattr(os, "geteuid"):
        return getattr(os, "geteuid")() == 0
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def mark_as_hidden(file: str) -> None:
    """Mark the given file as hidden."""
    current: int = Str(file).attrs()
    changed: int = current | stat.FILE_ATTRIBUTE_HIDDEN
    ctypes.windll.kernel32.SetFileAttributesW(Str(file).abs(), changed)


def mark_as_not_processed(parent: str, files: List[str]) -> None:
    """Mark the given files as unprocessed."""
    for file in files:
        x.NOT_PROCESSED.update({file: create_output(parent=parent, file=file)})


def save_to_cache_as_done(file: str) -> None:
    """Save the hash of the given file to the cache."""
    try:
        with open(consts.FILE_CACHE, "a", encoding=U8, errors=XML) as cache:
            cache.write(Str(file).sha256() + "\n")
    except OSError as err:
        if errors.osraise(errors.ENOENT, err=err):
            raise


def shutdown() -> None:
    """Shutdown the computer when the operation is finished."""
    cmd: List[str] = ["shutdown"]

    if OS.nt:
        msg: str = "AVsub operation complete!"
        cmd += ["/s", "/t", str(x.OPTS.shut * 60), "/d", "p:0:0", "/c", msg]
    else:
        cmd += ["-P", str(x.OPTS.shut)]

    try:
        avsubprocess(cmd, call=True)
        now: datetime = datetime.now()
        x_minutes_from_now: datetime = now + timedelta(minutes=x.OPTS.shut)
        date_format: str = "%H:%M:%S"
        after: str = format(x_minutes_from_now, date_format)
        print("[*] PC will shut down in", f"{x.OPTS.shut} minutes ({after})")
    except (FileNotFoundError, CalledProcessError, TimeoutExpired):
        print("[x] Cannot shut down PC or there is a pending shut down")


def shutdown_cancel() -> str:
    """Cancel a pending shutdown."""
    if "--shutdown-cancel" in sys.argv:
        try:
            avsubprocess(["shutdown", "/a" if OS.nt else "-c"], call=True)
        except (FileNotFoundError, CalledProcessError, TimeoutExpired):
            return "[x] Cannot cancel or there is no pending shut down"
        else:
            return "[+] Shut down cancelled"
    return ""
