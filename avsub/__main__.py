# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub - A simplified command-line interface for FFmpeg."""

import os
import sys
import shutil
import signal
import tempfile
from avsub import cli, core, ffmpeg, new


def setup_py_main():
    if sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty():
        if core.linux:
            if os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno()):
                sys.exit(1)
        main()
        clean()
    else:
        sys.exit(1)


def main():
    for sig in core.all_signals:
        signal.signal(sig, clean)  # Set the handler for signal "sig"

    if len(sys.argv) == 1:  # avsub: N1102
        print("No arguments specified, checking for updates...")
        sys.exit(new.check_for_updates())

    parser = cli.create_parser()
    opts = parser.parse_args()
    setattr(core, "opts", opts)  # Set attribute for "Over Control"

    for condition, error in cli.check_opts(opts).values():
        if condition:
            sys.exit(error)

    fff = ffmpeg.FFmpeg(opts)
    fff.build()  # Start creating the ultimate FFmpeg command

    # "The" TEMP folder for storing all other TEMP folders
    the_temp = core.join(tempfile.gettempdir(), under="AVsub")  # avsub: C1022
    try:
        # Create "the" TEMP folder
        os.makedirs(the_temp, exist_ok=True)
        # Create "a" new TEMP folder
        a_temp = tempfile.mkdtemp(prefix="avsub-", dir=the_temp)
    except (FileExistsError, FileNotFoundError, PermissionError):
        sys.exit("The required TEMP folder(s) could not be created (fatal)")

    # MANUAL OPERATION
    if core.path_exists(opts.input, check_isfile=True):
        # HARDSUB MANUAL OPERATION?
        if opts.embed:
            # Note: TEMP subtitle name to -almost- solve the escaping nonsense
            tempsub = core.join(a_temp, under=a_temp)

            # Store as {None: output} to delete TEMP subtitle on exit
            core.del_on_exit_temp.update({None: tempsub})
            try:
                # Copy the subtitle to TEMP folder as TEMP subtitle
                shutil.copyfile(core.abspath(opts.embed), tempsub)
            except (FileNotFoundError, PermissionError):
                sys.exit("The required TEMP file could not be created (fatal)")

            # Add a new level of escaping for TEMP subtitle path
            tempsub_escaped = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_force_style(filename=tempsub_escaped)

        files = [core.abspath(opts.input)]
    # AUTOMATIC OPERATION
    else:
        print("Getting files...")
        files = core.get_files(opts.input)  # Get all files to process
        if not files:
            sys.exit("Exiting, no files to process with current arguments")

    setattr(core, "a_temp", a_temp)  # Set attribute for "Over Control"
    ffmpeg.execute(fff.cmd, files=files)  # Start the operation


def clean(*args):
    for sig in core.all_signals:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the signal "sig"

    if not hasattr(core, "a_temp"):  # avsub: F1020
        sys.exit(1)

    print("\n")
    for member in core.del_on_exit:
        print("Not completed: '%s'" % core.basename(member))
    for member in core.not_processed:
        print("Not processed: '%s'" % core.basename(member))
    if getattr(core, "fatal_ffmpeg", False):
        print("Fatal, FFmpeg: '%s'" % getattr(core, "fatal_ffmpeg"))  # avsub: C1101
    print()

    if core.del_on_exit or core.del_on_exit_temp:
        print("Cleaning in progress, please do not interrupt...")
        core.del_del_on_exits(*[core.del_on_exit, core.del_on_exit_temp])

    if core.path_exists(getattr(core, "a_temp"), check_isdir=True):
        # If TEMP folder is not empty...
        if os.listdir(getattr(core, "a_temp", False)):
            print("Output folder: '%s'" % getattr(core, "a_temp"))
            if core.windows:  # avsub: C1023
                # Open TEMP folder
                os.startfile(getattr(core, "a_temp"), "open")  # avsub: F1100

    if args and args[0]:
        sys.exit("Exiting, received signal %d\a" % args[0])
    sys.exit("Done, exiting\a")


if __name__ == "__main__":
    setup_py_main()
