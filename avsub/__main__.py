# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
AVsub - A simplified command-line interface for FFmpeg.
"""

import datetime
import os
import shutil
import signal
import string
import subprocess
import sys
import tempfile
from subprocess import CalledProcessError
from subprocess import TimeoutExpired

from avsub import cli
from avsub import ffmpeg
from avsub import new
from avsub.core import consts
from avsub.core import x
from avsub.core.tools import cleaner
from avsub.core.tools import get_files
from avsub.core.tools import mark_as_not_processed
from avsub.str import Str


def setup_py_main():
    if sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty():
        if consts.POSIX:
            if os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno()):
                sys.exit(2)
        main()
        if x.RUN:
            stop()
        clean()
    else:
        sys.exit(2)


def checker():
    if len(sys.argv) == 1:
        print("[*] No arguments specified, checking for updates...")
        status = new.check_for_updates()
        sys.exit(status)

    parser = cli.create_parser()
    x.OPTS = parser.parse_args()

    gotcha = False

    for condition, error, priority in cli.check_opts(x.OPTS):
        if x.OPTS.bypass and priority == "W":
            continue
        if condition:
            print("[%s]" % priority, error)
            gotcha = True  # avsub: C2006

    if gotcha:
        sys.exit(2)

    if not ffmpeg.check():  # avsub: N2102
        print("[F] FFmpeg could not be executed")
        sys.exit(3)


def main():
    for sig in consts.ALL_SIGNALS:
        signal.signal(sig, stop)

    checker()

    fff = ffmpeg.FFmpeg()
    fff.build()

    try:
        x.THE_TEMP = Str(x.OPTS.temp).abs()
        os.makedirs(x.THE_TEMP, exist_ok=True)
        x.A_TEMP = tempfile.mkdtemp(prefix="avsub-", dir=x.THE_TEMP)
    except (FileNotFoundError, PermissionError) as err:
        print(err)
        print("[F] Required TEMP folder(s) could not be created")
        sys.exit(3)

    # MANUAL OPERATION?
    if Str(x.OPTS.input).isfile():
        files = [Str(x.OPTS.input).abs()]
        # HARDSUB MANUAL OPERATION?
        if x.OPTS.embed:
            # Note: New TEMP subtitle to -almost- avoid the escaping nonsense
            tempsub = Str(x.A_TEMP).join(x.A_TEMP)
            x.DEL_ON_EXIT_TEMP.update({tempsub: tempsub})

            try:
                shutil.copyfile(Str(x.OPTS.embed).abs(), tempsub)
            except (FileNotFoundError, PermissionError) as err:
                print(err)
                print("[F] Required TEMP subtitle could not be created")
                sys.exit(3)

            # Add a new level of escaping for TEMP subtitle pathname
            tempsub_escaped = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_hardsub(subpath=tempsub_escaped)
    # AUTOMATIC OPERATION?
    else:
        print("[*] Getting files...")
        files = get_files(parent=x.OPTS.input)
        if not files:
            print("[-] Exiting, no files to process with current arguments")
            sys.exit(2)

    print("[*] Getting ready to start...")
    mark_as_not_processed(parent=x.A_TEMP, files=files)

    x.FULL_CLEAN_AFTER_STOP = True
    ffmpeg.execute(fff.cmd, files=files)


def stop(*args):
    for sig in consts.ALL_SIGNALS:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the signal "sig"

    x.RUN = False  # Tell the program to stop

    if args and args[0]:
        x.SIGNAL_NUMBER = args[0]

    if not x.FULL_CLEAN_AFTER_STOP:
        cleaner(x.DEL_ON_EXIT_TEMP)
        sys.exit(2)


def logger():
    log = []
    status = 0

    for member in x.SUCCEEDED:
        message = string.Template("[+] Job completed: '$member'")
        print(message.substitute(member=Str(member).base()))
        log.append(message.substitute(member=Str(member).abs()))
    for member in x.DEL_ON_EXIT:
        message = string.Template("[-] Not completed: '$member'")
        print(message.substitute(member=Str(member).base()))
        log.append(message.substitute(member=Str(member).abs()))
        status = 2
    for member in x.NOT_PROCESSED:
        message = string.Template("[ ] Not processed: '$member'")
        print(message.substitute(member=Str(member).base()))
        log.append(message.substitute(member=Str(member).abs()))
        status = 2
    if x.FATAL_FFMPEG is not None:
        message = string.Template("[F] Fatal, FFmpeg: '$member'")
        print(message.substitute(member=Str(x.FATAL_FFMPEG).base()))
        log.append(message.substitute(member=Str(x.FATAL_FFMPEG).abs()))
        status = 3

    if x.OPTS.log:
        try:
            with open(Str(x.THE_TEMP).join(x.A_TEMP + ".log"),
                      "a",
                      encoding="utf-8",
                      errors="xmlcharrefreplace") as file:
                date = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
                line = "-" * len(date)
                file.write("+{0}+\n|{1}|\n+{0}+\n".format(line, date))
                for message in log:
                    file.write(message + "\n")
        except (FileNotFoundError, PermissionError) as err:
            print("[!] Logging error:", err)
        else:
            print("[*] Results saved: '%s'" % Str(file.name).abs())

    return status


def clean():
    line = "-" * os.get_terminal_size().columns

    print("\n")
    print(line)
    status = logger()
    print(line)

    if x.SIGNAL_NUMBER is not None:
        print("[x] Received a signal:", x.SIGNAL_NUMBER)
    if status != 0 or x.DEL_ON_EXIT_TEMP:
        print("[*] Cleaning, please do not interrupt", end="...", flush=True)
        cleaner(x.DEL_ON_EXIT, x.DEL_ON_EXIT_TEMP)
        print("DONE")
        print(line)

    succeeded = len(x.SUCCEEDED)
    failed = len(x.DEL_ON_EXIT) + len(x.NOT_PROCESSED)
    total = succeeded + failed

    print("SUMMARY")
    print("-------")
    print("Total:", total)
    print("Successful:", succeeded)
    print("Unsuccessful:", failed)
    print("Output folder: '%s'" % x.A_TEMP)
    print(line)
    print("Thanks for using AVsub|")
    print("----------------------+\a")

    if x.A_TEMP is not None:
        if Str(x.A_TEMP).isdir():
            if any([
                x.OPTS.no_open_dir == "never",
                x.OPTS.no_open_dir == "empty" and Str(x.A_TEMP).isfull(),
            ]):
                if consts.WINDOWS:
                    os.startfile(x.A_TEMP, "open")
                else:  # avsub: C2005
                    try:
                        subprocess.check_call(["xdg-open", x.A_TEMP],
                                              timeout=5,
                                              stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
                    except FileNotFoundError:
                        pass
                    except (CalledProcessError, TimeoutExpired):
                        pass

    sys.exit(status)  # Exit status (0: All is well, 2: Error, 3: Fatal)


if __name__ == "__main__":
    setup_py_main()
