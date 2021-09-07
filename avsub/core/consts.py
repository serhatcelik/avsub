# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This file contains constants.
"""

import signal
import urllib.error
from collections import defaultdict as safedict
from subprocess import CalledProcessError, TimeoutExpired
from typing import DefaultDict, Dict, List, Optional

from avsub import NT, OS, POSIX

##########
# Signal #
##########
_SIGBREAK: Optional[int] = signal.SIGBREAK if OS[NT] else None
_SIGINT: int = signal.SIGINT  # Interrupt from keyboard
_SIGQUIT: Optional[int] = signal.SIGQUIT if OS[POSIX] else None
ALL_SIGNALS: List[int] = [_ for _ in (_SIGINT, _SIGQUIT, _SIGBREAK) if _]

###################
# Argument Choice #
###################
AC: Dict[str, int] = {"mono": 1, "stereo": 2}  # Audio channel manipulation
ALIGN: Dict[str, int] = {
    "bleft": 1, "bottom": 2, "bright": 3,
    "tleft": 5, "top": 6, "tright": 7,
    "mleft": 9, "middle": 10, "mright": 11,
}  # Subtitle positions (Alignments) on screen
C1: Dict[str, str] = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML PrimaryColour codes in BBGGRR format
C2: Dict[str, str] = C1  # HTML OutlineColour codes in BBGGRR format
CRF: range = range(52)  # Constant Rate Factor values for video compression
LOGLEVEL: DefaultDict[int, int] = safedict(lambda: 40, {0: 16, 1: 24, 2: 32})

####################
# Exception Choice #
####################
_EXCEPTION_SUBPROCESS: tuple = (CalledProcessError, TimeoutExpired)
EXCEPTION_BY_FUNCTION: Dict[str, tuple] = {
    "avsub.new.check_for_updates": (ValueError, urllib.error.URLError),
    "avsub.ffmpeg.check": (FileNotFoundError, *_EXCEPTION_SUBPROCESS),
}
