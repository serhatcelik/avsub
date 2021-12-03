# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""Global "over control" variables (Xs) for handling external modules."""

from __future__ import absolute_import

from argparse import Namespace
from typing import Dict, List

A_TEMP: str  # TEMP folder for storing output files
CMD_TO_SHOW: str
DEL_ON_EXIT: Dict[str, str] = {}  # Files to be deleted on exit
DEL_ON_EXIT_TEMP: Dict[str, str] = {}  # TEMP files to be deleted on exit
DEL_ON_EXIT_TEMP_FOLDER: List[str] = []  # TEMP folders to be deleted on exit
FATAL_FFMPEG: Dict[str, str] = {}  # Encountered fatal FFmpeg errors
FULL_CLEAN_AFTER_STOP: bool = False
LOG_FILE: str
NOT_PROCESSED: Dict[str, str] = {}  # Unprocessed items
OPTS: Namespace  # Parsed command-line arguments
OUTS: str  # TEMP folder for storing output folders
RUN: bool = True  # Value that decides whether the program will continue to run
RUN_FFMPEG: bool = True  # Value that decides whether FFmpeg will be executed
SIG_INFO: list  # Captured signal name and number
SUCCEEDED: Dict[str, str] = {}  # Successfully completed items
THE_TEMP: str  # TEMP folder for storing all other TEMP folders
