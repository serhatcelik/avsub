# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This file contains constants.
"""

import collections
import os
import signal

############
# Platform #
############
POSIX = os.name == "posix"
WINDOWS = not POSIX

##########
# Signal #
##########
_SIGBREAK = signal.SIGBREAK if WINDOWS else None
_SIGINT = signal.SIGINT  # Interrupt from keyboard
_SIGQUIT = signal.SIGQUIT if POSIX else None  # Quit from keyboard
ALL_SIGNALS = [_ for _ in (_SIGINT, _SIGQUIT, _SIGBREAK) if _]

###################
# Argument Choice #
###################
AC = {"mono": "1", "stereo": "2"}  # Audio channel manipulation values
ALIGNMENT = {
    "bleft": "1", "bottom": "2", "bright": "3",
    "tleft": "5", "top": "6", "tright": "7",
    "mleft": "9", "middle": "10", "mright": "11",
}  # Subtitle positions on screen
CRF = range(52)  # Constant Rate Factor values for video compression
LOGLEVEL = collections.defaultdict(lambda: 40, {0: 16, 1: 24, 2: 32})
OUTLINECOLOUR = {
    "black": "&H000000&", "blue": "&HFF0000&", "brown": "&H2A2AA5&",
    "gray": "&H808080&", "green": "&H008000&", "orange": "&H00A5FF&",
    "pink": "&HCBC0FF&", "purple": "&H800080&", "red": "&H0000FF&",
    "white": "&HFFFFFF&", "yellow": "&H00FFFF&",
}  # HTML color codes in BBGGRR format
PRIMARYCOLOUR = OUTLINECOLOUR
