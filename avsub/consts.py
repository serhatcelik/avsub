"""This file contains constants."""

import collections

############
# Argument #
############
CHOICES_CHANNEL = {'mono': '1', 'stereo': '2'}  # Audio channel manipulation
CHOICES_SPEED = {
    '1/8': .5,
    '1/4': .5,
    '1/2': .5,
    '1': 2.,
    '2': 2.,
    '4': 2.,
    '8': 2.,
}
CHOICES_SUB_ALIGNMENT = {'bottom': '2', 'middle': '10', 'top': '6'}
CHOICES_SUB_BGR_CHART = {
    'black': '&H000000&',
    'green': '&H00FF00&',
    'white': '&HFFFFFF&',
}  # HTML color codes in BGR format

LOGLEVEL = collections.defaultdict(
    lambda: 'debug', {0: 'warning', 1: 'info', 2: 'verbose'}
)

#################
# Miscellaneous #
#################
X = '-'  # Placeholder for command-line arguments
