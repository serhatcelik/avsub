# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
Global variables and functions for handling external modules.
"""

import collections
import os
import re
import signal
import stat

from typing import Union

################
# Over Control #
################
RUN = True  # Value that determines whether the program will continue to run
FULL_CLEAN_AFTER_STOP = False

OPTS = None  # Parsed command-line arguments
A_TEMP = None
CMD_TO_SHOW = None
FATAL_FFMPEG = None
SIGNAL_NUMBER = None  # Captured signal number

DEL_ON_EXIT = dict()  # Container for storing items to be deleted on exit
DEL_ON_EXIT_TEMP = dict()
NOT_PROCESSED = dict()  # Container for storing unprocessed items

#############
# Platforms #
#############
LINUX = os.name == "posix"
WINDOWS = not LINUX  # Note: Does not include WSL (Windows Subsystem for Linux)

#######################
# Regular Expressions #
#######################
RE_HIDDEN_LINUX = r"^\."  # Starts with a dot
RE_EXTENSION = r"^([a-zA-Z0-9]+)$"  # Only letters and numbers

###########
# Signals #
###########
SIGINT = signal.SIGINT  # Interrupt from keyboard
SIGQUIT = signal.SIGQUIT if LINUX else None  # Quit from keyboard
SIGBREAK = signal.SIGBREAK if WINDOWS else None
ALL_SIGNALS = [_ for _ in [SIGINT, SIGQUIT, SIGBREAK] if _]

###########
# Choices #
###########
ACS = {"mono": "1", "stereo": "2"}  # Channels for audio channel manipulation
ALIGNMENTS = {
    "bleft": "1", "bottom": "2", "bright": "3",
    "tleft": "5", "top": "6", "tright": "7",
    "mleft": "9", "middle": "10", "mright": "11",
}  # Subtitle positions on screen
COLORS = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML color codes in BBGGRR format
LOGLEVELS = collections.defaultdict(lambda: "verbose")  # Log verbosity levels
LOGLEVELS.update({0: "error", 1: "warning", 2: "info", 3: "verbose"})


#########
# Tools #
#########
def abspath(path: str) -> str:
    return os.path.abspath(path)  # "path" will be normalized and absolutized


def basename(path: str) -> str:
    return os.path.basename(abspath(path))


def join(top: str, under: str) -> str:
    return os.path.join(abspath(top), basename(under))


def endswithext(text: str, ext: str) -> bool:
    return text.endswith(".%s" % ext.strip("."))


def path_exists(path: str,
                check_isfile: bool = False,
                check_isdir: bool = False) -> bool:
    """
    Check if the given path exists.

    :param path: Path to check.
    :param check_isfile: Check if the given path is an existing file.
    :param check_isdir: Check if the given path is an existing folder.
    """

    if check_isfile:
        return os.path.isfile(abspath(path))
    if check_isdir:
        return os.path.isdir(abspath(path))
    return os.path.exists(abspath(path))


def get_ext(name: str) -> str:
    if globals()["OPTS"].ext != "-":
        return globals()["OPTS"].ext
    return os.path.splitext(basename(name))[-1].strip(".")


def is_ext(ext: str) -> bool:
    """
    Check if the given extension is valid.

    :param ext: Extension to check.
    """

    return bool(re.search(RE_EXTENSION, ext)) or ext == "-"


def is_hidden(path: str) -> bool:
    """
    Check if the given path is hidden.

    :param path: Path to check.
    """

    if LINUX:
        # Note: Because of "abspath" in "basename", "." and ".." are not hidden
        return bool(re.search(RE_HIDDEN_LINUX, basename(path)))  # avsub: C1100

    try:
        stat_result = os.stat(abspath(path))
    except (FileNotFoundError, PermissionError):  # avsub: F1201
        return False
    # Note: Root folders such as "C:\" and "D:\" are considered hidden
    return bool(stat_result.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def get_files(top: str, check_full: bool = False) -> Union[bool, list]:
    try:
        files = [join(top, under=_) for _ in os.listdir(abspath(top))]
    except (FileNotFoundError, NotADirectoryError, PermissionError) as err:  # avsub: F1201
        if not check_full:
            print(err)
        return []
    else:
        if check_full:
            return bool(files)

    ext_exclude = set(globals()["OPTS"].exclude)
    ext_only = set(globals()["OPTS"].oext)

    for file in files.copy():
        if True in [
            path_exists(file, check_isdir=True),
            not globals()["OPTS"].hidden and is_hidden(file),
            any(endswithext(file, _) for _ in ext_exclude),
            ext_only and (not any(endswithext(file, _) for _ in ext_only)),
        ]:
            files.remove(file)

    return files


def create_output(top: str, file: str) -> str:
    """
    Create an output from input for the ultimate FFmpeg command.

    :param top: Top folder for output.
    :param file: Original input.
    """

    ext_basename = basename(file)
    no_ext_basename = os.path.splitext(ext_basename)[0]

    if globals()["OPTS"].ext == "-":
        return join(top, under=ext_basename)  # avsub: C1200
    return join(top, under=".".join([no_ext_basename, globals()["OPTS"].ext]))


def mark_as_not_processed(top: str, files: list) -> None:
    for file in files:  # avsub: C1020
        if not RUN:
            return
        NOT_PROCESSED.update({file: create_output(top, file=file)})


def cleaner(*args: dict) -> None:
    """
    Delete files that to be deleted on exit.

    :param args: Containers that store items to be deleted on exit.
    """

    for dictionary in args:
        for file in dictionary.values():
            try:
                os.remove(file)  # Delete the file
            except (FileNotFoundError, PermissionError):
                pass
            except OSError as err:
                # 22: Invalid argument
                if err.errno == 22:
                    pass
