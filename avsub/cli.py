"""Command-line interface."""

import argparse

from avsub.consts import CHANNEL, SUB_ALIGNMENT, SUB_BGR_CHART, X
from avsub.version import __version__

parser = argparse.ArgumentParser(
    prog='avsub',
    usage='python -m %(prog)s [<extension> [<option> ...]]',
    description='AVsub — A simplified command-line interface for FFmpeg',
    epilog='https://github.com/serhatcelik/avsub',
    formatter_class=argparse.RawTextHelpFormatter,
    allow_abbrev=False,
)

burn = parser.add_argument_group('embed options')
misc = parser.add_argument_group('miscellaneous')

mutual = parser.add_mutually_exclusive_group()

########################
# Positional Arguments #
########################
parser.add_argument(
    'extension',
    help='output extension or -',
    metavar='extension',
)

###########
# Options #
###########
parser.add_argument(
    '--channel',
    choices=CHANNEL,
    help='set %(metavar)s as output audio channel (choices: %(choices)s)',
    metavar="CHANNEL",
    dest="channel",
)
parser.add_argument(
    '--codec-audio', '-a',
    help='set %(metavar)s as output audio codec',
    metavar='CODEC',
    dest='codec_a',
)
parser.add_argument(
    '--codec-subtitle', '-s',
    help='set %(metavar)s as output subtitle codec',
    metavar='CODEC',
    dest='codec_s',
)
parser.add_argument(
    '--codec-video', '-v',
    help='set %(metavar)s as output video codec',
    metavar='CODEC',
    dest='codec_v',
)
parser.add_argument(
    '--compress', '-C',
    nargs='?',
    const=28,
    default=23,
    type=int,
    choices=range(0, 52),
    help='set %(metavar)s as crf value for compression (const: %(const)s)',
    metavar='VALUE',
    dest='compress',
)
parser.add_argument(
    '--copy', '-c',
    nargs='+',
    default=[],
    choices=[X, 'audio', 'subtitle', 'video'],
    help='use copy codec for output %(metavar)s stream (choices: %(choices)s)',
    metavar='STREAM',
    dest='copy',
)
parser.add_argument(
    '--disable-select',
    action='store_true',
    help='do not select all streams',
    dest='disable',
)
parser.add_argument(
    '--ffmpeg-list', '-f',
    help='provide %(metavar)s as an ffmpeg argument list',
    metavar='ARGS',
    dest='ffmpeg_list',
)
mutual.add_argument(
    '--only-audio', '-A',
    action='store_const',
    const=['-dn', '-sn', '-vn'],
    default=[],
    help='choose audio stream only',
    dest='only_a',
)
mutual.add_argument(
    '--only-subtitle', '-S',
    action='store_const',
    const=['-an', '-dn', '-vn'],
    default=[],
    help='choose subtitle stream only',
    dest='only_s',
)
mutual.add_argument(
    '--only-video', '-V',
    action='store_const',
    const=['-an', '-dn', '-sn'],
    default=[],
    help='choose video stream only',
    dest='only_v',
)
parser.add_argument(
    '--remove', '-r',
    nargs='+',
    default=[],
    choices=['audio', 'data', 'subtitle', 'video'],
    help='do not copy %(metavar)s stream to output (choices: %(choices)s)',
    metavar='STREAM',
    dest='remove',
)
parser.add_argument(
    '--remove-chapters',
    action='store_true',
    help='remove chapters',
    dest='chapters',
)
parser.add_argument(
    '--remove-metadata',
    action='store_true',
    help='remove metadata',
    dest='metadata',
)
parser.add_argument(
    '--trim',
    nargs=6,
    type=int,
    choices=range(0, 60),
    help='extract a part of a video',
    metavar=('H:', 'M:', 'S:', ':H', ':M', ':S'),
    dest='trim',
)

####################
# Subtitle Options #
####################
burn.add_argument(
    '--burn',
    action='store_true',
    help='burn a subtitle into a video',
    dest='burn',
)
burn.add_argument(
    '--color-outline',
    default='black',
    choices=SUB_BGR_CHART,
    help='set %(metavar)s as subtitle outline color (choices: %(choices)s)',
    metavar='COLOR',
    dest='color_outline',
)
burn.add_argument(
    '--color-primary',
    default='white',
    choices=SUB_BGR_CHART,
    help='set %(metavar)s as subtitle primary color (choices: %(choices)s)',
    metavar='COLOR',
    dest='color_primary',
)
burn.add_argument(
    '--font-name',
    default='',
    help='set %(metavar)s as subtitle font name',
    metavar='NAME',
    dest='font_name',
)
burn.add_argument(
    '--font-size',
    default=16,
    type=int,
    help='set %(metavar)s as subtitle font size (default: %(default)s)',
    metavar='SIZE',
    dest='font_size',
)
burn.add_argument(
    '--position',
    default='bottom',
    choices=SUB_ALIGNMENT,
    help='set %(metavar)s as subtitle position (choices: %(choices)s)',
    metavar='POSITION',
    dest='alignment',
)

#################
# Miscellaneous #
#################
misc.add_argument(
    '--shutdown',
    nargs='?',
    const=0,
    type=int,
    help='shut down the machine after %(metavar)s seconds (const: %(const)s)',
    metavar='TIMEOUT',
    dest='shutdown',
)
misc.add_argument(
    '--verbose', '-i',
    action='count',
    default=0,
    help='show more informative messages, can be used multiple times',
    dest='loglevel',
)
misc.add_argument(
    '--version',
    action='version',
    help='show program version and exit',
    version=__version__,
)
