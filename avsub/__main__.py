# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
AVsub - A simplified command-line interface for FFmpeg.
"""

import argparse
import os
import shutil
import signal
import string
import sys
import tempfile
from datetime import datetime
from typing import List

from avsub import cli, ffmpeg, new
from avsub.core import consts, x
from avsub.core.tools import dcleaner, dopen, fcleaner, get_files
from avsub.core.tools import is_a_foreground, is_a_tty, mark_as_not_processed
from avsub.str import Str


def setup_py_main() -> None:
    if is_a_tty() and is_a_foreground():
        main()
        if x.RUN:
            stop()
        clean()
    else:
        sys.exit(34)  # You know what it is ;)


def checker() -> None:
    if len(sys.argv) == 1:
        print("[*] No options specified, checking for updates...")
        if not new.check_for_updates():
            print("[!] Could not check for updates, try again later")
            sys.exit(2)
        sys.exit(0)

    parser: argparse.ArgumentParser = cli.create_parser()
    x.OPTS = parser.parse_args()

    gotcha: bool = False

    for condition, error, priority in cli.check_opts(x.OPTS):
        if x.OPTS.bypass and priority == "W":
            continue
        if condition:
            print("[%s]" % priority, error)
            gotcha: bool = True  # avsub: C2006

    if gotcha:
        sys.exit(2)

    print("[*] Starting a run test for FFmpeg...")
    if not ffmpeg.check():  # avsub: N2102
        print("[F] Could not execute FFmpeg")
        if not x.OPTS.no_err_exit:
            sys.exit(3)


def main() -> None:
    for sig in consts.ALL_SIGNALS:
        signal.signal(sig, stop)

    checker()

    fff: ffmpeg.FFmpeg = ffmpeg.FFmpeg()
    fff.build()

    try:
        x.THE_TEMP = Str(x.OPTS.temp).abs()
        os.makedirs(x.THE_TEMP, exist_ok=True)
        x.A_TEMP = tempfile.mkdtemp(prefix="avsub-", dir=x.THE_TEMP)
        x.DEL_ON_EXIT_TEMP_FOLDER.append(x.A_TEMP)
    except (FileNotFoundError, PermissionError) as err:
        print(err)
        print("[F] Required TEMP folders could not be created")
        sys.exit(3)
    else:
        x.LOG_FILE = Str(x.THE_TEMP).join("%s.log" % x.A_TEMP)

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
            except (FileNotFoundError, PermissionError) as err:
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
        files: List[str] = get_files(parent=x.OPTS.input)
        if not files:
            print("[-] Exiting, no files to process with current options")
            dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
            sys.exit(2)

    print("[*] Getting ready to start...")
    mark_as_not_processed(parent=x.A_TEMP, files=files)

    x.FULL_CLEAN_AFTER_STOP = True
    ffmpeg.execute(fff.cmd, files=files)


def stop(*args) -> None:
    for sig in consts.ALL_SIGNALS:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the signal "sig"

    x.RUN = False  # Tell the program to stop

    if args and args[0]:
        x.SIGNAL_NUMBER = args[0]

    if not x.FULL_CLEAN_AFTER_STOP:
        fcleaner(x.DEL_ON_EXIT_TEMP)
        dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
        sys.exit(2)


def logger() -> int:
    log: List[str] = []
    status: int = 0

    for member in x.SUCCEEDED:
        msg: string.Template = string.Template("[+] Job completed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
    for member in x.DEL_ON_EXIT:
        if member in x.FATAL_FFMPEG:  # avsub: C2203
            continue
        msg: string.Template = string.Template("[-] Not completed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status: int = 2
    for member in x.NOT_PROCESSED:
        msg: string.Template = string.Template("[ ] Not processed: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status: int = 2
    for member in x.FATAL_FFMPEG:
        msg: string.Template = string.Template("[F] Fatal, FFmpeg: '$member'")
        print(msg.substitute(member=Str(member).base()))
        log.append(msg.substitute(member=Str(member).abs()))
        status: int = 3

    xml: str = "xmlcharrefreplace"

    if x.OPTS.log:
        try:
            with open(x.LOG_FILE, "a", encoding="utf-8", errors=xml) as file:
                date: str = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
                line: str = Str("-").line(col=len(date))
                file.write("+{0}+\n|{1}|\n+{0}+\n".format(line, date))
                log.reverse()  # avsub: C2200
                for message in log:
                    file.write(message + "\n")
        except (FileNotFoundError, PermissionError) as err:
            print("[!] Logging error:", err)
        else:
            print("[*] Results saved: '%s'" % file.name)

    return status


def clean() -> None:
    line: str = Str("-").line()

    print("\n")
    print(line)
    status: int = logger()
    print(line)

    if hasattr(x, "SIGNAL_NUMBER"):
        print("[x] Received a signal:", x.SIGNAL_NUMBER)
    if status != 0 or x.DEL_ON_EXIT_TEMP:
        print("[*] Cleaning, please do not interrupt", end="...", flush=True)
        fcleaner(x.DEL_ON_EXIT, x.DEL_ON_EXIT_TEMP)
        if x.OPTS.no_open_dir != "never" and not x.OPTS.log:
            dcleaner(x.DEL_ON_EXIT_TEMP_FOLDER)
        print("DONE")
        print(line)

    succeeded: int = len(x.SUCCEEDED)
    failed: int = len(x.DEL_ON_EXIT) + len(x.NOT_PROCESSED)
    fatal: int = len(x.FATAL_FFMPEG)
    total: int = succeeded + failed

    print("SUMMARY")
    print("-------")
    print("Total:", total)
    print("Successful:", succeeded)
    print("Unsuccessful:", failed, "(%d fatal)" % fatal)
    print("Output folder: '%s'" % x.A_TEMP)
    print(line)
    print("Thanks for using AVsub|")
    print("----------------------+\a")

    dopen(x.A_TEMP)
    sys.exit(status)  # Exit status (0: All is well, 2: Error, 3: Fatal)


if __name__ == "__main__":
    setup_py_main()
