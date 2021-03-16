# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import os
import re
import stat
import signal
import platform

################
# Over Control #
################
not_processed = dict()  # Container for storing unprocessed items

del_on_exit = dict()  # Container for storing items to be deleted on exit
del_on_exit_temp = dict()

############
# Platform #
############
linux = os.name == "posix"  # GNU/Linux
wsl = linux and "microsoft" in platform.version().lower()  # WSL

###########
# Signals #
###########
sigquit = signal.SIGQUIT if linux else None  # pylint: disable=E1101
sigtstp = signal.SIGTSTP if linux else None  # pylint: disable=E1101
sigbreak = signal.SIGBREAK if not linux else None  # pylint: disable=E1101

signals = [i for i in [signal.SIGINT, sigquit, sigtstp, sigbreak] if i]

###########
# Choices #
###########
alignments = {
    "bleft": "1", "bottom": "2", "bright": "3", "tleft": "5", "top": "6",
    "tright": "7", "mleft": "9", "middle": "10", "mright": "11",
}  # Subtitle positions on screen
colors = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML color codes in BGR format


#############
# Utilities #
#############
def abspath(path):
    return os.path.abspath(path)


def basename(path):
    return os.path.basename(abspath(path))


def join(top, file):
    return os.path.join(abspath(top), basename(file))


def path_exists(path, check_isfile=False, check_isdir=False):
    """
    Checks if the given path exists.

    :param path: Path to check.
    :param check_isfile: Checks if the given path is an existing file.
    :param check_isdir: Checks if the given path is an existing folder.
    """

    if check_isfile:
        return os.path.isfile(abspath(path))
    if check_isdir:
        return os.path.isdir(abspath(path))
    return os.path.exists(abspath(path))


def is_hidden(path):
    """
    Checks if the given path is hidden.

    :param path: Path to check.
    """

    # Note: Root folders such as "C:\", "D:\" or "/" are considered hidden

    if linux:
        # Note: "." and ".." are not considered hidden
        return not bool(re.search(r"^([^.].*|\.{1,2})$", basename(path)))

    stat_result = os.stat(abspath(path))
    return bool(stat_result.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def is_ext(ext):
    """
    Checks if the given extension is valid.

    :param ext: Extension to check.
    """

    # Note: Only letters and numbers are allowed
    return bool(re.search(r"^[a-zA-Z0-9]+$", ext))


def list_files(top):
    """
    Retrieves files from the top folder.

    :param top: Top folder containing files.
    """

    files = [join(top, file=i) for i in os.listdir(abspath(top))]

    for path in files.copy():
        if True in [
            not path_exists(path, check_isfile=True),
            not globals()["opts"].hidden and is_hidden(path),
        ]:
            files.remove(path)

    return files


def create_output(top, file):
    """
    Creates an output from input for the FFmpeg command.

    :param top: Top folder for output.
    :param file: Original input.
    """

    no_ext_basename = os.path.splitext(basename(file))[0]

    return join(top, file=".".join([no_ext_basename, globals()["opts"].ext]))


def del_del_on_exit():
    del_on_exit.update(del_on_exit_temp)  # Update with TEMP files

    for member in del_on_exit:
        try:
            os.remove(del_on_exit[member])
        except (PermissionError, FileNotFoundError):
            pass
