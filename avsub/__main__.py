# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub - A simplified command-line interface for FFmpeg."""

# pylint: disable=consider-using-f-string

from __future__ import absolute_import

import os
import shutil
import sys
import tempfile
from argparse import ArgumentParser
from datetime import datetime
from string import Template
from typing import List

from avsub import cli, ffmpeg, new
from avsub.core import consts, errors, x
from avsub.core.tools import SigHandler, dcleaner, dopen, fcleaner, get_files
from avsub.core.tools import is_a_foreground, is_a_tty, mark_as_not_processed
from avsub.ffmpeg import FFmpeg
from avsub.str import Str


def setup_py_main() -> None:
    """Main function for setup script."""
    if is_a_tty() and is_a_foreground():
        main()
        if x.RUN:
            stop()
        clean()
    else:
        sys.exit(34)  # You know what it is ;)


def checker() -> None:
    """Docstring."""
    if len(sys.argv) == 1:
        print("[*] No options specified, checking for updates...")
        if not new.check_for_updates():
            print("[!] Could not check for updates, try again later")
            sys.exit(2)
        sys.exit(0)

    parser: ArgumentParser = cli.create_parser()
    x.OPTS = parser.parse_args()

    gotcha: bool = False

    for condition, error, priority in cli.check_opts(x.OPTS):
        if x.OPTS.bypass and priority == "W":
            continue
        if condition:
            print(f"[{priority}]", error)
            gotcha = True  # avsub: C2006

    if gotcha:
        sys.exit(2)

    print("[*] Starting a run test for FFmpeg...")
    if not ffmpeg.check():  # avsub: N2102
        print("[F] Could not execute FFmpeg")
        if not x.OPTS.no_err_exit:
            sys.exit(3)


def main() -> None:
    """Main function."""
    SigHandler(consts.SIGNALS).capture(stop)
    checker()

    fff: FFmpeg = ffmpeg.FFmpeg()
    fff.build()  # Start creating the ultimate FFmpeg command

    try:
        x.THE_TEMP = Str(x.OPTS.temp).abs()
        os.makedirs(x.THE_TEMP, exist_ok=True)
        x.A_TEMP = tempfile.mkdtemp(prefix="avsub-", dir=x.THE_TEMP)
        x.DEL_ON_EXIT_TEMP_FOLDER.append(x.A_TEMP)
    except OSError as err:  # avsub: F2210,F2220
        if errors.osraise(errors.EEXIST, errors.ENOENT, err=err):
            raise
        print(err)
        print("[F] Required TEMP folders could not be created")
        sys.exit(3)
    else:
        x.LOG_FILE = Str(x.THE_TEMP).join(f"{x.A_TEMP}.log")

    # MANUAL OPERATION?
    if Str(x.OPTS.input).isfile():
        files: List[str] = [Str(x.OPTS.input).abs()]
        # HARDSUB MANUAL OPERATION?
        if x.OPTS.embed:
            # Note: New TEMP subtitle to -almost- avoid the escaping nonsense
            tempsub: str = Str(x.A_TEMP).join(x.A_TEMP)
            x.DEL_ON_EXIT_TEMP.update({tempsub: tempsub})

            try:
                shutil.copyfile(Str(x.OPTS.embed).abs(), tempsub)
            except OSError as err:
                if errors.osraise(errors.ENOENT, err=err):
                    raise
                print(err)
                print("[F] Required TEMP subtitle could not be created")
                dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
                sys.exit(3)

            # Add a new level of escaping for TEMP subtitle pathname
            sub_escaped: str = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_hardsub(subpath=sub_escaped)
    # AUTOMATIC OPERATION?
    else:
        print("[*] Getting files...")
        files = get_files(parent=x.OPTS.input)
        if not files:
            print("[-] Exiting, no files to process with current options")
            dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
            sys.exit(2)

    print("[*] Getting ready to start...")
    mark_as_not_processed(parent=x.A_TEMP, files=files)

    x.FULL_CLEAN_AFTER_STOP = True
    ffmpeg.execute(fff.cmd, files=files)


def stop(*args) -> None:
    """Docstring."""
    SigHandler(consts.SIGNALS).ignore()

    x.RUN = False  # Tell the program to stop

    if args:
        x.SIGNAL_NUMBER = args[0]

    if not x.FULL_CLEAN_AFTER_STOP:
        fcleaner(x.DEL_ON_EXIT_TEMP)
        dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
        sys.exit(2)


def logger() -> int:
    """Docstring."""
    log: List[str] = []
    status: int = 0

    for member in x.SUCCEEDED:
        msg: Template = Template("[+] Job completed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
    for member in x.DEL_ON_EXIT:
        if member in x.FATAL_FFMPEG:  # avsub: C2203
            continue
        msg = Template("[-] Not completed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status = 2
    for member in x.NOT_PROCESSED:
        msg = Template("[ ] Not processed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status = 2
    for member in x.FATAL_FFMPEG:
        msg = Template("[F] Fatal, FFmpeg: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status = 3

    xml: str = "xmlcharrefreplace"

    if x.OPTS.log:
        try:
            with open(x.LOG_FILE, "a", encoding="utf-8", errors=xml) as file:
                date: str = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
                line: str = Str("=").line(col=len(date))
                file.write("{0}\n{1}\n{0}\n".format(line, date))
                log.reverse()  # avsub: C2200
                for message in log:
                    file.write(message + "\n")
        except OSError as err:
            if errors.osraise(errors.ENOENT, err=err):
                raise
            print("[!] Logging error:", err)
        else:
            print("[*] Results saved: '%s'" % file.name)

    return status


def clean() -> None:
    """Show the log, do the cleaning and exit the program."""
    print("\n")
    print(Str("-").line())
    status: int = logger()
    print(Str("-").line())

    if hasattr(x, "SIGNAL_NUMBER"):
        print("[x] Received a signal:", x.SIGNAL_NUMBER)
    if status != 0 or x.DEL_ON_EXIT_TEMP:
        print("[*] Cleaning, please do not interrupt", end="...", flush=True)
        fcleaner(x.DEL_ON_EXIT, x.DEL_ON_EXIT_TEMP)
        if x.OPTS.no_open_dir != "never" and not x.OPTS.log:
            dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
        print("DONE")
        print(Str("-").line())

    succeeded: int = len(x.SUCCEEDED)
    failed: int = len(x.DEL_ON_EXIT) + len(x.NOT_PROCESSED)
    fatal: int = len(x.FATAL_FFMPEG)
    total: int = succeeded + failed
    folder: str = x.A_TEMP if (x.A_TEMP and Str(x.A_TEMP).isdir()) else ""
    thanks: str = "Thanks for using AVsub"

    print("SUMMARY")
    print("-------")
    print("Total:", total)
    print("Successful:", succeeded)
    print("Unsuccessful:", failed, "(%d fatal)" % fatal)
    print("Output folder: '%s'" % folder)
    print(Str("-").line())
    print("{0}|\n{1}+\a".format(thanks, Str("-").line(col=len(thanks))))

    dopen(x.A_TEMP)
    sys.exit(status)  # Exit status (0: All is well, 2: Error, 3: Fatal)


if __name__ == "__main__":
    setup_py_main()
