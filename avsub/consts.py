"""This file contains constants."""

import sys
from collections import defaultdict

LINUX = sys.platform.startswith('linux')

WINDOWS = sys.platform.startswith('win32')

X = '-'  # Placeholder for command-line arguments

CHANNEL = {'mono': 1, 'stereo': 2}  # Audio channel manipulation

LOGLEVEL = defaultdict(lambda: 48, {0: 24, 1: 32, 2: 40})

SUB_ALIGNMENT = {'bottom': 2, 'middle': 10, 'top': 6}

SUB_BGR_CHART = {
    'black': '&H000000&',
    'green': '&H00FF00&',
    'white': '&HFFFFFF&',
}  # HTML color codes in BGR format
