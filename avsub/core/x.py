# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
Global "over control" variables (Xs) for handling external modules.
"""

A_TEMP = None
CMD_TO_SHOW = None
DEL_ON_EXIT = dict()  # Container for items to be deleted on exit
DEL_ON_EXIT_TEMP = dict()  # Container for TEMP items to be deleted on exit
FATAL_FFMPEG = None
FULL_CLEAN_AFTER_STOP = False
NOT_PROCESSED = dict()  # Container for unprocessed items
OPTS = None  # Parsed command-line arguments
RUN = True  # Value that determines whether the program will continue to run
RUN_FFMPEG = True  # Value that determines whether FFmpeg will be executed
SIGNAL_NUMBER = None  # Captured signal number
SUCCEEDED = dict()  # Container for successfully completed items
