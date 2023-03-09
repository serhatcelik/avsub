"""This file contains constants."""

from collections import defaultdict

X = '-'  # Placeholder for command-line arguments

LOGLEVEL = defaultdict(lambda: 48, {0: 24, 1: 32, 2: 40})

SUBTITLE_ALIGNMENT = {'bottom': 2, 'middle': 10, 'top': 6}

SUBTITLE_BGR_CHART = {
    'black': '&H000000&',
    'green': '&H00FF00&',
    'white': '&HFFFFFF&',
}  # HTML color codes in BGR format
