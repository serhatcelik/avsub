# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This file contains constants."""

from __future__ import absolute_import

import signal
import urllib.error
from collections import defaultdict as safedict
from subprocess import CalledProcessError, TimeoutExpired
from typing import DefaultDict, Dict, List, Tuple

##########
# Signal #
##########
_SIGBREAK: str = "SIGBREAK"
_SIGINT: str = "SIGINT"  # Interrupt from keyboard
_SIGQUIT: str = "SIGQUIT"  # Quit from keyboard
_ALL_SIGNALS: Tuple[str, ...] = (_SIGBREAK, _SIGINT, _SIGQUIT)
SIGNALS: List[int] = []
for sig in _ALL_SIGNALS:
    if hasattr(signal, sig) and hasattr(getattr(signal, sig), "value"):
        SIGNALS.append(getattr(signal, sig).value)

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

####################
# Exception Choice #
####################
_EXCEPTION_SUBPROCESS: tuple = (CalledProcessError, TimeoutExpired)
EXCEPTION_BY_FUNCTION: Dict[str, tuple] = {
    "avsub.new.check_for_updates": (ValueError, urllib.error.URLError),
    "avsub.ffmpeg.check": (FileNotFoundError, *_EXCEPTION_SUBPROCESS),
}
