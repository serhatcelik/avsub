"""This file contains constants."""

from collections import defaultdict

############
# Argument #
############
CHANNEL = {'mono': '1', 'stereo': '2'}  # Audio channel manipulation
LOGLEVEL = defaultdict(lambda: 'verbose', {0: 'warning', 1: 'info'})
SUBTITLE_ALIGNMENT = {'bottom': '2', 'middle': '10', 'top': '6'}
SUBTITLE_BGR_CHART = {
    'black': '&H000000&',
    'green': '&H00FF00&',
    'white': '&HFFFFFF&',
}  # HTML color codes in BGR format

#################
# Miscellaneous #
#################
X = '-'  # Placeholder for command-line arguments
