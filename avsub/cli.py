# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import argparse
from avsub import __license__, core


def create_parser():
    parser = argparse.ArgumentParser(
        prog="avsub",
        description="AVsub : A simplified CLI for FFmpeg\n"
                    "Written by Serhat Çelik "
                    "(with the help of my family and a friend)",
        epilog="This tool is for very basic operations only. "
               "If you need advanced operations, use FFmpeg instead.\n"
               "See https://github.com/serhatcelik/avsub "
               "for more information.",
        formatter_class=argparse.RawTextHelpFormatter, prefix_chars="+-",
    )

    ########################
    # Positional Arguments #
    ########################
    parser.add_argument("input", metavar="INPUT", help="input file or folder")
    parser.add_argument("ext", metavar="EXTENSION", help="output extension")

    ######################
    # Optional Arguments #
    ######################
    parser.add_argument(
        "+a", metavar="CODEC",
        dest="acodec", help="set CODEC as output audio codec",
    )
    parser.add_argument(
        "-A", "--audio", dest="oaudio", action="store_const", default=[],
        const=["-vn", "-sn", "-dn"], help="choose audio stream(s) only",
    )
    parser.add_argument(
        "--compress", metavar="VALUE", dest="crf",
        type=int, help="set VALUE as crf value to compress input",
    )
    parser.add_argument(
        "--copy", metavar="STREAM",
        nargs="+", default=[], choices=["audio", "video", "sub", "all"],
        help="use copy codec for output STREAM instead of another codec",
    )
    parser.add_argument(
        "-H", "--hidden", action="store_true",
        help="include hidden input (note: root folders are considered hidden)",
    )
    parser.add_argument(
        "-i", "--inform", dest="loglevel", action="store_const", const="info",
        default="warning", help="show informative messages during processing",
    )
    parser.add_argument(
        "-L", "--license", action="version",
        version=__license__.__doc__, help="show license and exit",
    )
    parser.add_argument(
        "--remove", metavar="STREAM", nargs="+",
        default=[], choices=["audio", "video", "sub", "metadata", "chapters"],
        help="do not copy STREAM from input to output",
    )
    parser.add_argument(
        "+s", metavar="CODEC",
        dest="scodec", help="set CODEC as output subtitle codec",
    )
    parser.add_argument(
        "--speed", metavar="PRESET",
        dest="preset", choices=["faster", "fast", "medium", "slow", "slower"],
        help="set PRESET as encoding speed",
    )
    parser.add_argument(
        "-S", "--subtitle", dest="osubtitle", action="store_const", default=[],
        const=["-an", "-vn", "-dn"], help="choose subtitle stream(s) only",
    )
    parser.add_argument(
        "+v", metavar="CODEC",
        dest="vcodec", help="set CODEC as output video codec",
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=__license__.VERSION, help="show program version and exit",
    )
    parser.add_argument(
        "-V", "--video", dest="ovideo", action="store_const", default=[],
        const=["-an", "-sn", "-dn"], help="choose video stream(s) only",
    )

    ######################
    # Subtitle Arguments #
    ######################
    group = parser.add_argument_group("subtitle arguments")

    group.add_argument(
        "-b", "--box", dest="BorderStyle", action="store_const",
        const="3", default="1", help="add an opaque box around subtitle",
    )
    group.add_argument(
        "--color1", metavar="COLOR",
        dest="PrimaryColour", default="white", choices=core.colors,
        help="set COLOR as subtitle primary color [default: %(default)s]",
    )
    group.add_argument(
        "--color2", metavar="COLOR",
        dest="OutlineColour", default="black", choices=core.colors,
        help="set COLOR as subtitle outline color [default: %(default)s]",
    )
    group.add_argument(
        "--embed", metavar="SUBTITLE", help="embed SUBTITLE into video",
    )
    group.add_argument(
        "--font", metavar="NAME",
        dest="FontName", default="", help="set NAME as subtitle font name",
    )
    group.add_argument(
        "--position", metavar="POSITION",
        dest="Alignment", default="bottom", choices=core.alignments,
        help="set POSITION as subtitle alignment [default: %(default)s]",
    )
    group.add_argument(
        "--size", metavar="VALUE", dest="FontSize", type=int, default=18,
        help="set VALUE as subtitle font size [default: %(default)s]",
    )

    return parser


def check_opts(opts):
    return True not in [
        "audio" in opts.remove and bool(opts.oaudio),
        "video" in opts.remove and bool(opts.ovideo),
        "sub" in opts.remove and bool(opts.osubtitle),
        bool(opts.oaudio) and bool(opts.ovideo),
        bool(opts.oaudio) and bool(opts.osubtitle),
        bool(opts.ovideo) and bool(opts.osubtitle),
        "audio" in opts.copy and bool(opts.acodec),
        "video" in opts.copy and bool(opts.vcodec),
        "sub" in opts.copy and bool(opts.scodec),
        "all" in opts.copy and bool(opts.acodec),
        "all" in opts.copy and bool(opts.vcodec),
        "all" in opts.copy and bool(opts.scodec),
        bool(opts.embed) and "video" in opts.copy,
        bool(opts.embed) and "all" in opts.copy,
        not opts.hidden and core.is_hidden(opts.input),
        not opts.hidden and bool(opts.embed) and core.is_hidden(opts.embed),
    ]
