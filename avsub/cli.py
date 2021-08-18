# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This module contains functions for command-line parsing.
"""

import argparse
import string
import tempfile

from avsub import __license__
from avsub.__license__ import AUTHOR
from avsub.__license__ import VERSION
from avsub.core import consts
from avsub.str import Str


def create_parser():
    parser = argparse.ArgumentParser(
        prog="avsub", usage="%(prog)s [input extension [extra_arguments]]",
        description=f"AVsub - A simplified command-line interface for FFmpeg\n"
                    f"Written by {AUTHOR} "
                    f"(with the help of my family and a friend)",
        epilog="This tool is for basic operations only. "
               "If you need advanced operations, use FFmpeg instead.\n"
               "See https://github.com/serhatcelik/avsub "
               "for more information.",
        formatter_class=argparse.RawTextHelpFormatter, prefix_chars="+-",
    )

    group_hardsub = parser.add_argument_group("hardsub arguments")
    group_independent = parser.add_argument_group("independent arguments")

    mutual_group_0 = parser.add_mutually_exclusive_group()
    mutual_group_1 = group_independent.add_mutually_exclusive_group()

    ########################
    # Positional Arguments #
    ########################
    parser.add_argument(
        "input", metavar="input", action="store", help="input file or folder",
    )
    parser.add_argument(
        "ext", metavar="extension", action="store",
        help=f"output extension ('-' for input file extension);\n"
             f"\tValid chars: {string.digits}_-\n"
             f"\t             {string.ascii_lowercase}\n"
             f"\t             {string.ascii_uppercase}",
    )

    ######################
    # Optional Arguments #
    ######################
    parser.add_argument(
        "+a", metavar="<CODEC>", dest="acodec", action="store", default=None,
        help="set %(metavar)s as output audio codec",
    )
    mutual_group_0.add_argument(
        "-A", "--audio", dest="oaudio", action="store_const", default=[],
        const=["-vn", "-sn", "-dn"], help="choose audio stream(s) only",
    )
    parser.add_argument(
        "--channel", metavar="<CHANNEL>", dest="ac", action="store",
        default=None, choices=consts.AC,
        help="set %(metavar)s as output audio channel;\n"
             "\tChoices: %(choices)s",
    )
    parser.add_argument(
        "-C", "--compress", metavar="<VALUE>", dest="crf", action="store",
        nargs="?", default=None, const=30, type=int, choices=consts.CRF,
        help=f"set %(metavar)s as crf value to compress video;\n"
             f"\tConstant: %(const)s\n"
             f"\tChoices: {consts.CRF[0]}-{consts.CRF[-1]}",
    )
    parser.add_argument(
        "-c", "--copy", metavar="<STREAM>", dest="copy", action="store",
        nargs="+", default=[], choices=["audio", "video", "sub", "all"],
        help="use copy codec for output %(metavar)s instead of another;\n"
             "\tChoices: %(choices)s",
    )
    parser.add_argument(
        "-f", metavar="<ARGS>", dest="custom_ffmpeg", action="store",
        default=None,
        help="provide %(metavar)s as an ffmpeg argument list (be careful!)",
    )
    parser.add_argument(
        "--no-map-all", dest="no_map_all", action="store_true", default=False,
        help="disable choosing all streams (may cause data loss)",
    )
    parser.add_argument(
        "--remove", metavar="<STREAM>", dest="remove", action="store",
        nargs="+", default=[],
        choices=["audio", "video", "sub", "metadata", "chapters"],
        help="do not copy %(metavar)s from input to output;\n"
             "\tChoices: %(choices)s",
    )
    parser.add_argument(
        "+s", metavar="<CODEC>", dest="scodec", action="store", default=None,
        help="set %(metavar)s as output subtitle codec",
    )
    parser.add_argument(
        "--speed", metavar="<PRESET>", dest="preset", action="store",
        nargs="?", default=None, const="fast",
        choices=["faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="set %(metavar)s as video encoding speed;\n"
             "\tConstant: %(const)s\n"
             "\tChoices: %(choices)s",
    )  # avsub: N2001,C2000
    mutual_group_0.add_argument(
        "-S", "--subtitle", dest="osubtitle", action="store_const", default=[],
        const=["-an", "-vn", "-dn"], help="choose subtitle stream(s) only",
    )
    parser.add_argument(
        "--trim", metavar=("<FROM>", "<TO>"), dest="trim", action="store",
        nargs=2, default=None, type=int,
        help="extract a portion of input from sec <FROM> to <TO>",
    )
    parser.add_argument(
        "+v", metavar="<CODEC>", dest="vcodec", action="store", default=None,
        help="set %(metavar)s as output video codec",
    )
    mutual_group_0.add_argument(
        "-V", "--video", dest="ovideo", action="store_const", default=[],
        const=["-an", "-sn", "-dn"], help="choose video stream(s) only",
    )

    #####################
    # Hardsub Arguments #
    #####################
    group_hardsub.add_argument(
        "-b", "--box", dest="BorderStyle", action="store_const", default=None,
        const="3", help="add an opaque box around subtitle",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--color1", metavar="<COLOR>", dest="PrimaryColour", action="store",
        default=None, choices=consts.PRIMARYCOLOUR,
        help="set %(metavar)s as subtitle primary color",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--color2", metavar="<COLOR>", dest="OutlineColour", action="store",
        default=None, choices=consts.OUTLINECOLOUR,
        help="set %(metavar)s as subtitle outline color",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "-e", "--embed", metavar="<SUBTITLE>", dest="embed", action="store",
        default=None, help="embed %(metavar)s into video",
    )
    group_hardsub.add_argument(
        "--font", metavar="<NAME>", dest="FontName", action="store",
        default=None, help="set %(metavar)s as subtitle font name",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--position", metavar="<POSITION>", dest="Alignment", action="store",
        default=None, choices=consts.ALIGNMENT,
        help="set %(metavar)s as subtitle alignment",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--size", metavar="<VALUE>", dest="FontSize", action="store",
        default=None, type=int, help="set %(metavar)s as subtitle font size",
    )  # avsub: C2003

    #########################
    # Independent Arguments #
    #########################
    group_independent.add_argument(
        "-B", "--bypass", dest="bypass", action="store_true", default=False,
        help="skip checking some command-line arguments (not recommended)",
    )
    mutual_group_1.add_argument(
        "--exclude", metavar="<EXTENSION>", dest="exclude", action="store",
        nargs="+", default=[],
        help="do not process input if its extension is %(metavar)s",
    )
    group_independent.add_argument(
        "-F", "--ffmpeg", dest="show_ffmpeg", action="store_true",
        default=False, help="show the ffmpeg command during processing",
    )
    group_independent.add_argument(
        "-H", "--hidden", dest="hidden", action="store_true", default=False,
        help="include hidden/protected input",
    )
    group_independent.add_argument(
        "-i", "--inform", dest="loglevel", action="count", default=0,
        help=f"show more info, can be used up to {len(consts.LOGLEVEL)} times",
    )
    group_independent.add_argument(
        "-L", "--license", dest="license", action="version", default=None,
        version=__license__.__doc__, help="show license and exit",
    )
    group_independent.add_argument(
        "-l", "--log", dest="log", action="store_true", default=False,
        help="log results to a file inside the parent of the output folder",
    )  # avsub: N2101
    group_independent.add_argument(
        "--no-open-dir", metavar="<MODE>", dest="no_open_dir", action="store",
        nargs="?", default="empty" if consts.WINDOWS else "always",
        const="always", choices=["never", "empty", "always"],
        help="set %(metavar)s to change the output folder opening behavior;\n"
             "\tDefault: %(default)s\n"
             "\tConstant: %(const)s\n"
             "\tChoices: %(choices)s",
    )  # avsub: C2001,C2002,C2010
    mutual_group_1.add_argument(
        "--only", metavar="<EXTENSION>", dest="oext", action="store",
        nargs="+", default=[],
        help="process input only if its extension is %(metavar)s",
    )
    group_independent.add_argument(
        "-o", "--output", metavar="<FOLDER>", dest="temp", action="store",
        default=Str(tempfile.gettempdir()).join("AVsub"),
        help="set %(metavar)s as the parent of the output folder",
    )  # avsub: N2100
    group_independent.add_argument(
        "-v", "--version", dest="version", action="version", default=None,
        version=VERSION, help="show program version and exit",
    )

    return parser


def check_opts(opts):
    return [
        [
            all([all(_ not in opts.input for _ in ("/", "\\")),
                 opts.input != ".",
                 Str(opts.input).iscwd()]),
            "input ~ '%s': This is current folder, use '.'" % opts.input,
            "!",
        ],
        [
            all([all(_ not in opts.temp for _ in ("/", "\\")),
                 opts.temp != ".",
                 Str(opts.temp).iscwd()]),
            "-o/--output ~ '%s': This is current folder, use '.'" % opts.temp,
            "!",
        ],
        [
            not Str(opts.input).exists(),
            "input ~ '%s': No such file or folder" % opts.input,
            "!",
        ],
        [
            not Str(opts.ext).isext(),
            "extension ~ '%s': Not a valid format (see help)" % opts.ext,
            "!",
        ],
        [
            any(not Str(_).isext() for _ in opts.exclude),
            "extension: BANNED: --exclude: Contains invalid extension(s)",
            "!",
        ],
        [
            any(not Str(_).isext() for _ in opts.oext),
            "extension: BANNED: --only: Contains invalid extension(s)",
            "!",
        ],
        [
            opts.embed and not Str(opts.embed).isfile(),
            "-e/--embed ~ '%s': No such file" % opts.embed,
            "!",
        ],
        [
            opts.embed and Str(opts.input).isdir(),
            "-e/--embed: BANNED: input ~ '%s': This is a folder" % opts.input,
            "!",
        ],
        [
            not opts.hidden and Str(opts.input).ishidden(),
            "-H/--hidden: BANNED: input ~ '%s': Protected X" % opts.input,
            "!",
        ],
        [
            not opts.hidden and opts.embed and Str(opts.embed).ishidden(),
            "-H/--hidden: BANNED: -e/--embed ~ '%s': Protected X" % opts.embed,
            "!",
        ],
        [
            not opts.hidden and Str(opts.temp).ishidden(),
            "-H/--hidden: BANNED: -o/--output ~ '%s': Protected X" % opts.temp,
            "!",
        ],
        [
            opts.embed and ("video" in opts.copy or "all" in opts.copy),
            "-e/--embed: BANNED: -c/--copy {video | all}: Forbidden option",
            "W",
        ],
        [
            opts.embed and opts.vcodec == "copy",
            "-e/--embed: BANNED: +v copy: Forbidden option",
            "W",
        ],
        [
            opts.ac and ("audio" in opts.copy or "all" in opts.copy),
            "--channel: BANNED: -c/--copy {audio | all}: Meaningless option",
            "W",
        ],
        [
            opts.ac and opts.acodec == "copy",
            "--channel: BANNED: +a copy: Meaningless option",
            "W",
        ],
        [
            opts.oaudio and "audio" in opts.remove,
            "-A/--audio: BANNED: --remove audio: Mutually exclusive group",
            "W",
        ],
        [
            opts.ovideo and "video" in opts.remove,
            "-V/--video: BANNED: --remove video: Mutually exclusive group",
            "W",
        ],
        [
            opts.osubtitle and "sub" in opts.remove,
            "-S/--subtitle: BANNED: --remove sub: Mutually exclusive group",
            "W",
        ],
        [
            sum(1 for _ in ("audio", "video", "sub") if _ in opts.remove) == 3,
            "--remove audio video sub: Output contains no stream",
            "W",
        ],
        [
            opts.acodec and ("audio" in opts.copy or "all" in opts.copy),
            "+a: BANNED: -c/--copy {audio | all}: Mutually exclusive group",
            "W",
        ],
        [
            opts.vcodec and ("video" in opts.copy or "all" in opts.copy),
            "+v: BANNED: -c/--copy {video | all}: Mutually exclusive group",
            "W",
        ],
        [
            opts.scodec and ("sub" in opts.copy or "all" in opts.copy),
            "+s: BANNED: -c/--copy {sub | all}: Mutually exclusive group",
            "W",
        ],
        [
            opts.trim and opts.trim[0] < 0,
            "--trim: <FROM> value (1st) is negative",
            "W",
        ],
        [
            opts.trim and opts.trim[-1] <= opts.trim[0],
            "--trim: <TO> value (2nd) smaller than or equal to <FROM> value",
            "W",
        ],
        [
            opts.trim and ("video" in opts.copy or "all" in opts.copy),
            "--trim: BANNED: -c/--copy {video | all}: Meaningless option",
            "W",
        ],
        [
            opts.trim and opts.vcodec == "copy",
            "--trim: BANNED: +v copy: Meaningless option",
            "W",
        ],
    ]
