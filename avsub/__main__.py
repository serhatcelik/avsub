# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""AVsub : A simplified CLI for FFmpeg."""

import os
import sys
import shutil
import signal
import tempfile
import webbrowser
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
    parser = cli.create_parser()
    opts = parser.parse_args()
    setattr(core, "opts", opts)  # Set attribute for over control

    # Note: Check the existence of inputs first to prevent "FileNotFoundError"
    if not core.path_exists(opts.input):
        sys.exit("E : INPUT : '%s' : No such file or folder" % opts.input)
    elif opts.embed and not core.path_exists(opts.embed, check_isfile=True):
        sys.exit("E : SUBTITLE : '%s' : No such file" % opts.embed)
    elif not cli.check_opts(opts):
        sys.exit("E : Contradictory definitions when parsing the command-line")
    elif not core.is_ext(opts.ext):
        sys.exit("E : EXTENSION : '%s' : Not a valid format" % opts.ext)
    elif opts.embed and core.path_exists(opts.input, check_isdir=True):
        sys.exit("E : EMBED : INPUT : '%s' : This is a folder" % opts.input)

    for sig in core.signals:
        signal.signal(sig, clean)  # Set the handler for signal "sig"

    fff = ffmpeg.FFmpeg(opts)
    fff.build()  # Start creating the ultimate FFmpeg command

    try:
        # Create a new TEMP folder
        main.temp = tempfile.mkdtemp(prefix="avsub_")
    except PermissionError:
        sys.exit("F : TEMP folder could not be created")

    # MANUAL OPERATION
    if core.path_exists(opts.input, check_isfile=True):
        # HARDSUB MANUAL OPERATION?
        if opts.embed:
            # Note: New subtitle name to (almost) solve the escaping nonsense
            tempsub = core.join(main.temp, file=main.temp)

            # Store as {None : output} to delete the (TEMP) subtitle on exit
            core.del_on_exit_temp.update({None: tempsub})
            try:
                # Copy the subtitle to TEMP folder
                shutil.copyfile(core.abspath(opts.embed), tempsub)
            except (PermissionError, FileNotFoundError):
                sys.exit("F : '%s' : TEMP file could not be created" % tempsub)

            # Add a new level of escaping for the subtitle path
            tempsub_escaped = tempsub.replace("\\", "/").replace(":", "\\\\:")
            fff.build_force_style(filename=tempsub_escaped)

        files = [core.abspath(opts.input)]
    # AUTOMATIC OPERATION
    else:
        files = core.list_files(opts.input)  # Get all the files to process
        if not files:
            sys.exit("W : Exiting, no files to process")

    ffmpeg.execute(fff.cmd, top=main.temp, files=files)  # Start the operation


def clean(*args):  # pylint: disable=W0613
    for sig in core.signals:
        signal.signal(sig, signal.SIG_IGN)  # Simply ignore the "sig" signal

    print("\n")
    for member in list(core.not_processed) + list(core.del_on_exit):
        if member in core.not_processed:
            print("W : Not processed : '%s'" % core.basename(member))
        else:
            print("E : Not completed : '%s'" % core.basename(member))

    # Delete files in "del_on_exit" and "del_on_exit_temp" containers
    core.del_del_on_exit()

    if core.path_exists(getattr(main, "temp"), check_isdir=True):
        # If the folder is not empty...
        if os.listdir(getattr(main, "temp")):
            print("I : Output folder : '%s'" % getattr(main, "temp"))
            if not core.wsl:
                webbrowser.open(getattr(main, "temp"), new=0, autoraise=False)

    sys.exit("\a")


if __name__ == "__main__":
    setup_py_main()
