# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import argparse
from avsub import __license__, core


def create_parser():
    parser = argparse.ArgumentParser(
        prog="avsub",
        description="AVsub - A simplified command-line interface for FFmpeg\n"
                    "Written by Serhat Çelik "
                    "(with the help of my family and a friend)",
        epilog="This tool is for basic operations only. "
               "If you need advanced operations, use FFmpeg instead.\n"
               "See https://github.com/serhatcelik/avsub "
               "for more information.",
        formatter_class=argparse.RawTextHelpFormatter, prefix_chars="+-",
    )

    ########################
    # Positional Arguments #
    ########################
    parser.add_argument("input", help="input file or folder")
    parser.add_argument("ext", metavar="extension", help="output extension")

    ######################
    # Optional Arguments #
    ######################
    parser.add_argument(
        "+a", metavar="CODEC",
        dest="acodec", help="set CODEC as output audio codec",
    )
    parser.add_argument(
        "+s", metavar="CODEC",
        dest="scodec", help="set CODEC as output subtitle codec",
    )
    parser.add_argument(
        "+v", metavar="CODEC",
        dest="vcodec", help="set CODEC as output video codec",
    )
    parser.add_argument(
        "-A", "--audio", dest="oaudio", action="store_const", default=[],
        const=["-vn", "-sn", "-dn"], help="choose audio stream(s) only",
    )
    parser.add_argument(
        "--channel", metavar="CHANNEL", dest="ac",
        choices=core.acs, help="set CHANNEL as output audio channel",
    )  # avsub: N1100
    parser.add_argument(
        "--compress", metavar="VALUE", dest="crf",
        type=int, help="set VALUE as crf value to compress video",
    )
    parser.add_argument(
        "--copy", metavar="STREAM",
        nargs="+", default=[], choices=["audio", "video", "sub", "all"],
        help="use copy codec for output STREAM instead of another codec",
    )
    parser.add_argument(
        "-F", "--ffmpeg", dest="show_ffmpeg", action="store_true",
        help="show the ffmpeg command during processing (except hardsub)"
    )  # avsub: N1101
    parser.add_argument(
        "-H", "--hidden", action="store_true", help="include hidden input",
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
        "--speed", metavar="PRESET",
        dest="preset", choices=["faster", "fast", "medium", "slow", "slower"],
        help="set PRESET as video encoding speed",
    )
    parser.add_argument(
        "-S", "--subtitle", dest="osubtitle", action="store_const", default=[],
        const=["-an", "-vn", "-dn"], help="choose subtitle stream(s) only",
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
        default="1", const="3", help="add an opaque box around subtitle",
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
        "--size", metavar="VALUE", dest="FontSize", type=int, default=20,
        help="set VALUE as subtitle font size [default: %(default)s]",
    )  # avsub: C1021

    return parser


def check_opts(opts):
    return {
        0: [
            not core.path_exists(opts.input),
            "input ~ '%s': No such file or folder" % opts.input,
        ],
        1: [
            opts.embed and not core.path_exists(opts.embed, check_isfile=True),
            "embed ~ '%s': No such file" % opts.embed,
        ],
        2: [
            not core.is_ext(opts.ext),
            "extension ~ '%s': Not a valid format" % opts.ext,
        ],
        3: [
            opts.embed and core.path_exists(opts.input, check_isdir=True),
            "embed: input ~ '%s': This is a folder" % opts.input,
        ],
        4: [
            not opts.hidden and core.is_hidden(opts.input),
            "hidden: input ~ '%s': Hidden or root folder" % opts.input,
        ],
        5: [
            not opts.hidden and opts.embed and core.is_hidden(opts.embed),
            "hidden: embed ~ '%s': File is hidden" % opts.embed,
        ],
        6: [
            opts.ac and ("audio" in opts.copy or opts.acodec == "copy"),
            "channel: Contradictory with [ copy audio ]",
        ],
        7: [
            opts.ac and "all" in opts.copy,
            "channel: Contradictory with [ copy all ]",
        ],
        8: [
            "audio" in opts.remove and opts.oaudio,
            "remove ~ audio: Contradictory with [ only audio ]",
        ],
        9: [
            "video" in opts.remove and opts.ovideo,
            "remove ~ video: Contradictory with [ only video ]",
        ],
        10: [
            "sub" in opts.remove and opts.osubtitle,
            "remove ~ sub: Contradictory with [ only subtitle ]",
        ],
        11: [
            sum(1 for _ in ["audio", "video", "sub"] if _ in opts.remove) == 3,
            "remove ~ audio: Contradictory with [ remove video sub ]",
        ],
        12: [
            opts.oaudio and (opts.ovideo or opts.osubtitle),
            "audio: Contradictory with [ only video/subtitle ]",
        ],
        13: [
            opts.ovideo and opts.osubtitle,
            "video: Contradictory with [ only subtitle ]",
        ],
        14: [
            ("audio" in opts.copy or "all" in opts.copy) and opts.acodec,
            "copy ~ audio/all: Contradictory with [ codec audio ]",
        ],
        15: [
            ("video" in opts.copy or "all" in opts.copy) and opts.vcodec,
            "copy ~ video/all: Contradictory with [ codec video ]",
        ],
        16: [
            ("sub" in opts.copy or "all" in opts.copy) and opts.scodec,
            "copy ~ sub/all: Contradictory with [ codec subtitle ]",
        ],
        17: [
            opts.embed and ("video" in opts.copy or opts.vcodec == "copy"),
            "embed ~ '%s': Contradictory with [ copy video ]" % opts.embed,
        ],
        18: [
            opts.embed and "all" in opts.copy,
            "embed ~ '%s': Contradictory with [ copy all ]" % opts.embed,
        ],
    }
