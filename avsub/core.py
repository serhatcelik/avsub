# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""Global variables and functions for handling external modules."""

import os
import re
import stat
import signal

################
# Over Control #
################
# opts <- avsub.__main__.main
# a_temp <- avsub.__main__.main
# fatal_ffmpeg <- avsub.ffmpeg.execute

del_on_exit = dict()  # Container for storing items to be deleted on exit
del_on_exit_temp = dict()
not_processed = dict()  # Container for storing unprocessed items

############
# Platform #
############
linux = os.name == "posix"  # GNU/Linux
windows = not linux  # Microsoft Windows (not include WSL)

#######################
# Regular Expressions #
#######################
RE_HIDDEN_LINUX = r"^\..*"  # Starts with a dot
RE_EXTENSION = r"^([a-zA-Z0-9]+)$"  # Only letters and numbers

###########
# Signals #
###########
sigquit = signal.SIGQUIT if linux else None  # Quit from keyboard
sigtstp = signal.SIGTSTP if linux else None  # Stop typed at terminal
sigbreak = signal.SIGBREAK if not linux else None
all_signals = [_ for _ in [signal.SIGINT, sigquit, sigtstp, sigbreak] if _]

###########
# Choices #
###########
acs = {"mono": "1", "stereo": "2"}  # Channels for audio channel manipulation
alignments = {
    "bleft": "1", "bottom": "2", "bright": "3",
    "tleft": "5", "top": "6", "tright": "7",
    "mleft": "9", "middle": "10", "mright": "11",
}  # Subtitle positions on screen
colors = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML color codes in BBGGRR format


#########
# Tools #
#########
def abspath(path):
    return os.path.abspath(path)  # "path" will be normalized and absolutized


def basename(path):
    return os.path.basename(abspath(path))


def join(top, under):
    return os.path.join(abspath(top), basename(under))


def path_exists(path, check_isfile=False, check_isdir=False):
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


def is_ext(ext):
    return bool(re.search(RE_EXTENSION, ext))


def is_hidden(path):
    if linux:
        # Note: Because of "abspath" in "basename", "." and ".." are not hidden
        return bool(re.search(RE_HIDDEN_LINUX, basename(path)))  # avsub: C1100

    try:
        stat_result = os.stat(abspath(path))
    except FileNotFoundError:
        return False
    # Note: Root folders such as "C:\" and "D:\" are considered hidden
    return bool(stat_result.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def get_files(top):
    files = [join(top, under=_) for _ in os.listdir(abspath(top))]

    for file in files.copy():
        if True in [
            path_exists(file, check_isdir=True),
            not globals()["opts"].hidden and is_hidden(file),
        ]:
            files.remove(file)

    return files


def create_output(top, file):
    """
    Create an output from input for the ultimate FFmpeg command.

    :param top: Top folder for output.
    :param file: Original input.
    """

    no_ext_basename = os.path.splitext(basename(file))[0]

    return join(top, under=".".join([no_ext_basename, globals()["opts"].ext]))


def del_del_on_exits(*args):
    for dictionary in args:
        for key in dictionary:
            try:
                os.remove(dictionary[key])  # Delete the file
            except (FileNotFoundError, PermissionError):
                pass
