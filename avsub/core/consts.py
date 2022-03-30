# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This file contains constants."""

from __future__ import absolute_import

import signal
import tempfile
import urllib.error
from collections import defaultdict as safedict
from subprocess import CalledProcessError  # nosec
from subprocess import TimeoutExpired  # nosec
from typing import DefaultDict, Dict, List, Tuple

from avsub.core import notice_
from avsub.str import Str

##########
# Signal #
##########
_SIGBREAK: str = "SIGBREAK"
_SIGINT: str = "SIGINT"  # Interrupt from keyboard
_SIGQUIT: str = "SIGQUIT"  # Quit from keyboard
_ALL_SIGNALS: Tuple[str, ...] = (_SIGBREAK, _SIGINT, _SIGQUIT)
SIGNALS: Dict[str, int] = {}
for sig in _ALL_SIGNALS:
    if hasattr(signal, sig) and hasattr(getattr(signal, sig), "value"):
        SIGNALS.update({sig: getattr(signal, sig).value})

###################
# Argument Choice #
###################
AC: Dict[str, int] = {"mono": 1, "stereo": 2}  # Audio channel manipulation
ALIGN: Dict[str, int] = {
    "bleft": 1, "bottom": 2, "bright": 3,
    "tleft": 5, "top": 6, "tright": 7,
    "mleft": 9, "middle": 10, "mright": 11,
}  # Subtitle positions (Alignment) on screen
C1: Dict[str, str] = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML PrimaryColour codes in BBGGRR format
C2: Dict[str, str] = C1  # HTML OutlineColour codes in BBGGRR format
CRF: List[int] = list(range(0, 51 + 1))  # Constant Rate Factor values
LOGLEVEL: DefaultDict[int, int] = safedict(lambda: 40, {0: 16, 1: 24, 2: 32})
SHUT: List[int] = list(range(2, 60 + 1))  # Shutdown timeout (2min-1hour)

####################
# Exception Choice #
####################
_EXCEPTION_SUBPROCESS: tuple = (CalledProcessError, TimeoutExpired)
EXCEPTION_BY_FUNCTION: Dict[str, tuple] = {
    "avsub.new.check_for_updates": (ValueError, urllib.error.URLError),
    "avsub.ffmpeg.check": (FileNotFoundError, *_EXCEPTION_SUBPROCESS),
}

############
# Location #
############
DIR_THE_TEMP_DEF: str = Str(tempfile.gettempdir()).join("AVsub")
DIR_CONFS: str = Str(DIR_THE_TEMP_DEF).join("Confs")
DIR_LOGS: str = Str(DIR_THE_TEMP_DEF).join("Logs")  # avsub: C2300
FILE_CACHE: str = Str(DIR_CONFS).join("done.cache")
FILE_STARTUP: str = Str(DIR_CONFS).join("Audio-Video-Subtitle.bat")

###################
# Version Control #
###################
_URL_MAIN: str = notice_.URL
_URL_RAW: str = "https://raw.githubusercontent.com/serhatcelik/avsub"
_URL_RELEASES: str = _URL_MAIN + "/releases"
URL_LATEST: str = _URL_RELEASES + "/latest"
URL_TAG: str = _URL_RELEASES + "/tag/"  # Do not remove the trailing slash!
URL_YANKED: str = _URL_RAW + "/main/yanked.txt"

#####################
# Encoding Handling #
#####################
U8: str = "utf-8"
XML: str = "xmlcharrefreplace"  # Chars are replaced with the XML reference

####################
# Windows Registry #
####################
REG_KEY_RUN: str = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
REG_VAL_RUN: str = "\"" + FILE_STARTUP + "\""
