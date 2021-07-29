# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
AVsub - A simplified command-line interface for FFmpeg.
"""

import os
import shutil
import signal
import sys
import tempfile

from avsub import cli, core, ffmpeg, new


def setup_py_main():
    if sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty():
        if core.LINUX:
            if os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno()):
                sys.exit(2)
        main()
        if core.RUN:
            stop()
        clean()
    else:
        sys.exit(2)


def main():
    for sig in core.ALL_SIGNALS:
        signal.signal(sig, stop)

    if len(sys.argv) == 1:  # avsub: N1102
        print("[*] No arguments specified, checking for updates...")
        status = new.check_for_updates(retry=3, timeout=5)
        sys.exit(status)

    parser = cli.create_parser()
    opts = parser.parse_args()
    core.OPTS = opts  # Set attribute for "Over Control"

    for condition, error, priority in cli.check_opts(opts):
        if opts.bypass and (priority == "warning"):
            continue
        if any([condition] if not isinstance(condition, list) else condition):
            print("[!] %s" % error)
            sys.exit(2)

    fff = ffmpeg.FFmpeg(parsed_args=opts)
    fff.build()  # Start creating the ultimate FFmpeg command

    # "The" TEMP folder for storing all other TEMP folders
    the_temp = core.join(tempfile.gettempdir(), under="AVsub")  # avsub: C1022
    try:
        # Create "the" TEMP folder
        os.makedirs(the_temp, exist_ok=True)
        # Create "a" new TEMP folder
        a_temp = tempfile.mkdtemp(prefix="avsub-", dir=the_temp)
        core.A_TEMP = a_temp
    except (FileExistsError, FileNotFoundError, NotADirectoryError,
            PermissionError):
        print("[!] Required TEMP folder(s) could not be created (fatal)")
        sys.exit(3)

    # MANUAL OPERATION?
    if core.path_exists(opts.input, check_isfile=True):
        # HARDSUB MANUAL OPERATION?
        if opts.embed:
            # Note: New TEMP subtitle to -almost- avoid the escaping nonsense
            tempsub = core.join(a_temp, under=a_temp)

            # Store as {None: output} to delete TEMP subtitle on exit
            core.DEL_ON_EXIT_TEMP.update({None: tempsub})
            try:
                # Copy the subtitle to TEMP folder as TEMP subtitle
                shutil.copyfile(core.abspath(opts.embed), tempsub)
            except (FileNotFoundError, PermissionError):
                print("[!] Required TEMP file could not be created (fatal)")
                sys.exit(3)

            # Add a new level of escaping for TEMP subtitle path
            tempsub_escaped = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_force_style(subpath=tempsub_escaped)

        files = [core.abspath(opts.input)]
    # AUTOMATIC OPERATION?
    else:
        print("[*] Getting files...")
        files = core.get_files(top=opts.input)
        if not files:
            print("[-] Exiting, no files to process with current arguments")
            sys.exit(2)

    print("[*] Getting ready to start...")
    core.mark_as_not_processed(top=a_temp, files=files)

    core.FULL_CLEAN_AFTER_STOP = True
    ffmpeg.execute(fff.cmd, files=files)  # Start the operation


def stop(*args):  # avsub: F1200
    """
    Handle signals and tell the program to terminate itself.

    :param args: Container for signal number and current stack frame.
    """

    for sig in core.ALL_SIGNALS:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the signal "sig"

    core.RUN = False  # Tell the program to stop

    if args and args[0]:
        core.SIGNAL_NUMBER = args[0]

    if not core.FULL_CLEAN_AFTER_STOP:
        core.cleaner(core.DEL_ON_EXIT_TEMP)  # avsub: F1110
        sys.exit(2)


def clean():
    """
    Show the log, do the cleaning and exit the program.
    """

    status = 0  # Current exit status (0: All is well, 2: Error, 3: Fatal)

    print("\n")
    for member in core.DEL_ON_EXIT:
        status = 2
        print("[-] Not completed: '%s'" % core.basename(member))
    for member in core.NOT_PROCESSED:
        status = 2
        print("[ ] Not processed: '%s'" % core.basename(member))
    if core.FATAL_FFMPEG is not None:
        status = 3
        print("[!] Fatal, FFmpeg: '%s'" % core.FATAL_FFMPEG)  # avsub: C1101
    print()

    if core.SIGNAL_NUMBER is not None:
        print("[*] Received a signal: %d" % core.SIGNAL_NUMBER)
    if core.DEL_ON_EXIT or core.DEL_ON_EXIT_TEMP:
        print("[*] Cleaning in progress, please do not interrupt...")
        core.cleaner(core.DEL_ON_EXIT, core.DEL_ON_EXIT_TEMP)

    if core.A_TEMP is not None:
        if core.path_exists(core.A_TEMP, check_isdir=True):
            # If TEMP folder is not empty...
            if core.get_files(top=core.A_TEMP, check_full=True):
                print("[+] Output folder: '%s'" % core.A_TEMP)
                if core.WINDOWS and (not core.OPTS.no_open_dir):
                    os.startfile(core.A_TEMP, "open")  # avsub: F1100

    print("[*] Done, exiting\n"
          "~~~~~~~~~~~~~~~~~~~~~~~\n"
          "Thanks for using AVsub!\n"
          "~~~~~~~~~~~~~~~~~~~~~~~\a")
    sys.exit(status)


if __name__ == "__main__":
    setup_py_main()
