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
    parser.add_argument("ext", metavar="extension",
                        help="output extension ('-' for input file extension)")

    ######################
    # Optional Arguments #
    ######################
    mutual_group_0 = parser.add_mutually_exclusive_group()
    mutual_group_1 = parser.add_mutually_exclusive_group()
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
    mutual_group_0.add_argument(
        "-A", "--audio", dest="oaudio", action="store_const", default=[],
        const=["-vn", "-sn", "-dn"], help="choose audio stream(s) only",
    )
    parser.add_argument(
        "-B", "--bypass", dest="bypass", action="store_true",
        help="skip checking some command-line arguments (not recommended)",
    )  # avsub: N1203
    parser.add_argument(
        "--channel", metavar="CHANNEL", dest="ac",
        choices=core.acs, help="set CHANNEL as output audio channel",
    )  # avsub: N1100
    parser.add_argument(
        "--compress", metavar="VALUE", dest="crf",
        nargs="?", const=30, type=int, choices=range(0, 51 + 1),
        help="set VALUE as crf value to compress video [constant: %(const)s]",
    )  # avsub: C1202,C1203
    parser.add_argument(
        "--copy", metavar="STREAM", dest="copy",
        nargs="+", default=[], choices=["audio", "video", "sub", "all"],
        help="use copy codec for output STREAM instead of another codec",
    )
    mutual_group_1.add_argument(
        "--exclude", metavar="EXTENSION", dest="exclude", nargs="+",
        default=[], help="do not process input if its extension is EXTENSION",
    )  # avsub: N1201
    parser.add_argument(
        "-F", "--ffmpeg", dest="show_ffmpeg", action="store_true",
        help="show the ffmpeg command during processing (except hardsub)"
    )  # avsub: N1101
    parser.add_argument(
        "-H", "--hidden",
        dest="hidden", action="store_true", help="include hidden input",
    )
    parser.add_argument(
        "-i", "--inform", dest="loglevel", action="store_const", const="info",
        default="warning", help="show informative messages during processing",
    )
    parser.add_argument(
        "-L", "--license", dest="license", action="version",
        version=__license__.__doc__, help="show license and exit",
    )
    mutual_group_1.add_argument(
        "--only", metavar="EXTENSION", dest="oext", nargs="+",
        default=[], help="process input only if its extension is EXTENSION",
    )  # avsub: N1202
    parser.add_argument(
        "--remove", metavar="STREAM", dest="remove", nargs="+",
        default=[], choices=["audio", "video", "sub", "metadata", "chapters"],
        help="do not copy STREAM from input to output",
    )
    parser.add_argument(
        "--speed", metavar="PRESET",
        dest="preset", choices=["faster", "fast", "medium", "slow", "slower"],
        help="set PRESET as video encoding speed",
    )
    mutual_group_0.add_argument(
        "-S", "--subtitle", dest="osubtitle", action="store_const", default=[],
        const=["-an", "-vn", "-dn"], help="choose subtitle stream(s) only",
    )
    parser.add_argument(
        "--trim", metavar=("FROM", "TO"), dest="trim", nargs=2, type=int,
        help="extract a portion of input from second FROM to TO",
    )  # avsub: N1200
    parser.add_argument(
        "-v", "--version", dest="version", action="version",
        version=__license__.VERSION, help="show program version and exit",
    )
    mutual_group_0.add_argument(
        "-V", "--video", dest="ovideo", action="store_const", default=[],
        const=["-an", "-sn", "-dn"], help="choose video stream(s) only",
    )

    #####################
    # Hardsub Arguments #
    #####################
    group = parser.add_argument_group("hardsub arguments")
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
        "--embed", metavar="SUBTITLE",
        dest="embed", help="embed SUBTITLE into video",
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
    return [
        [
            False not in [all(_ not in opts.input for _ in ["/", "\\"]),
                          opts.input != ".",
                          core.abspath(opts.input) == core.abspath(".")],
            "input ~ '%s': Did you mean '.' (current folder)?" % opts.input,
            "error",
        ],  # avsub: F1203
        [
            not core.path_exists(opts.input),
            "input ~ '%s': No such file or folder" % opts.input,
            "error",
        ],
        [
            opts.embed and not core.path_exists(opts.embed, check_isfile=True),
            "embed ~ '%s': No such file" % opts.embed,
            "error",
        ],
        [
            not core.is_ext(opts.ext),
            "extension ~ '%s': Not a valid format" % opts.ext,
            "error",
        ],
        [
            opts.embed and core.path_exists(opts.input, check_isdir=True),
            "embed: input ~ '%s': This is a folder" % opts.input,
            "error",
        ],
        [
            not opts.hidden and core.is_hidden(opts.input),
            "hidden: input ~ '%s': Hidden or root folder" % opts.input,
            "error",
        ],
        [
            not opts.hidden and opts.embed and core.is_hidden(opts.embed),
            "hidden: embed ~ '%s': File is hidden" % opts.embed,
            "error",
        ],
        [
            [opts.ac and ("audio" in opts.copy or opts.acodec == "copy"),
             opts.ac and "all" in opts.copy],
            "channel: Not allowed with [ copy audio/all ]",
            "warning",
        ],
        [
            "audio" in opts.remove and opts.oaudio,
            "remove ~ audio: Not allowed with [ only audio ]",
            "warning",
        ],
        [
            "video" in opts.remove and opts.ovideo,
            "remove ~ video: Not allowed with [ only video ]",
            "warning",
        ],
        [
            "sub" in opts.remove and opts.osubtitle,
            "remove ~ sub: Not allowed with [ only subtitle ]",
            "warning",
        ],
        [
            sum(1 for _ in ["audio", "video", "sub"] if _ in opts.remove) == 3,
            "remove ~ audio: Not allowed with [ remove video sub ]",
            "warning",
        ],
        [
            ("audio" in opts.copy or "all" in opts.copy) and opts.acodec,
            "copy ~ audio/all: Not allowed with [ codec audio ]",
            "warning",
        ],
        [
            ("video" in opts.copy or "all" in opts.copy) and opts.vcodec,
            "copy ~ video/all: Not allowed with [ codec video ]",
            "warning",
        ],
        [
            ("sub" in opts.copy or "all" in opts.copy) and opts.scodec,
            "copy ~ sub/all: Not allowed with [ codec subtitle ]",
            "warning",
        ],
        [
            [opts.embed and ("video" in opts.copy or opts.vcodec == "copy"),
             opts.embed and "all" in opts.copy],
            "embed ~ '%s': Not allowed with [ copy video/all ]" % opts.embed,
            "warning",
        ],
        [
            opts.trim and (opts.trim[-1] <= opts.trim[0]),
            "trim: Error, TO value (2nd) smaller than or equal to FROM value",
            "warning",
        ],
        [
            [opts.trim and ("video" in opts.copy or opts.vcodec == "copy"),
             opts.trim and "all" in opts.copy],
            "trim: Not allowed with [ copy video/all ]",
            "warning",
        ],
    ]
