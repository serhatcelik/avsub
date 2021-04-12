# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub - A simplified command-line interface for FFmpeg."""

import os
import sys
import shutil
import signal
import tempfile
from avsub import cli, core, ffmpeg


def setup_py_main():
    if sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty():
        if core.linux:
            if os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno()):  # pylint: disable=E1101
                sys.exit(1)
        main()
        clean()
    else:
        sys.exit(1)


def main():
    for sig in core.signals:
        signal.signal(sig, clean)  # Set the handler for signal "sig"

    parser = cli.create_parser()
    opts = parser.parse_args()
    setattr(core, "opts", opts)  # Set attribute for "Over Control"

    # Note: Check the existence of inputs first to prevent "FileNotFoundError"
    if not core.path_exists(opts.input):
        sys.exit("INPUT -> '%s': No such file or folder" % opts.input)
    elif opts.embed and not core.path_exists(opts.embed, check_isfile=True):
        sys.exit("embed -> SUBTITLE -> '%s': No such file" % opts.embed)
    elif not core.is_ext(opts.ext):
        sys.exit("EXTENSION -> '%s': Not a valid format" % opts.ext)
    elif opts.embed and core.path_exists(opts.input, check_isdir=True):
        sys.exit("embed -> INPUT -> '%s': This is a folder" % opts.input)
    elif not cli.check_opts(opts):
        sys.exit("Contradictory options when parsing the command-line")

    fff = ffmpeg.FFmpeg(opts)
    fff.build()  # Start creating the ultimate FFmpeg command

    try:
        # The TEMP folder for storing all other TEMP folders
        the_temp = core.join(tempfile.gettempdir(), under="AVsub")  # C1022
        # Create the TEMP folder
        os.makedirs(the_temp, exist_ok=True)
        # Create a new TEMP folder
        main.temp = tempfile.mkdtemp(prefix="avsub_", dir=the_temp)
    except (FileNotFoundError, PermissionError):
        sys.exit("The required TEMP folder could not be created (fatal)")

    # MANUAL OPERATION
    if core.path_exists(opts.input, check_isfile=True):
        # HARDSUB MANUAL OPERATION?
        if opts.embed:
            # Note: TEMP subtitle name to -almost- solve the escaping nonsense
            tempsub = core.join(main.temp, under=main.temp)

            # Store as {None: output} to delete the TEMP subtitle on exit
            core.del_on_exit_temp.update({None: tempsub})
            try:
                # Copy the subtitle to TEMP folder as TEMP subtitle
                shutil.copyfile(core.abspath(opts.embed), tempsub)
            except (FileNotFoundError, PermissionError):
                sys.exit("The required TEMP file could not be created (fatal)")

            # Add a new level of escaping for the TEMP subtitle path
            tempsub_escaped = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_force_style(filename=tempsub_escaped)

        files = [core.abspath(opts.input)]
    # AUTOMATIC OPERATION
    else:
        files = core.get_files(opts.input)  # Get all files to process
        if not files:
            sys.exit("Exiting, no files to process with current options")

    ffmpeg.execute(fff.cmd, top=main.temp, files=files)  # Start the operation


def clean(*args):  # pylint: disable=W0613
    for sig in core.signals:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the signal "sig"

    print("\n")
    for member in core.del_on_exit:
        print("Not completed -> '%s'" % core.basename(member))
    for member in core.not_processed:
        print("Not processed -> '%s'" % core.basename(member))

    # Cleaning...
    core.del_del_on_exit(core.del_on_exit)
    core.del_del_on_exit(core.del_on_exit_temp)

    if hasattr(main, "temp"):  # F1020
        if core.path_exists(getattr(main, "temp"), check_isdir=True):
            # If the TEMP folder is not empty...
            if os.listdir(getattr(main, "temp")):
                print("Output folder -> '%s'" % getattr(main, "temp"))
                if core.windows:  # C1023
                    os.startfile(getattr(main, "temp"))  # Open the TEMP folder

        sys.exit("\a")


if __name__ == "__main__":
    setup_py_main()
