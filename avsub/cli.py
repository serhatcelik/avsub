# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

r"""
EXAMPLES
  1) Convert mkv to mp4
  avsub "input.mkv" mp4

  2) Convert all files in current directory to mp4 including hidden ones
  avsub . mp4 -H

  3) Copy video stream from input to output, keep input extension
  avsub "input.mp4" - -c video

  4) Convert mkv to mp4 with audio codec aac and video codec h264
  avsub "input.mkv" mp4 +a aac +v h264

  5) Convert mp4 to mp3 and choose audio stream (not other streams)
  avsub "input.mp4" mp3 -A

  6) Compress video with CRF (Constant Rate Factor) value of 35
  avsub "input.mp4" - -C 35

  7) Do not copy subtitle stream and metadata from input to output
  avsub "input.mp4" - --remove sub metadata

  8) Extract a part of video from 02:01:00 (or 7260) to 02:01:05 (or 7265)
  avsub "input.mp4" - --trim 02:01:00 02:01:05

  9) Embed subtitle into video (hardsub) with font name Arial and font size 25
  avsub "input.mp4" - -e "input.srt" --font "Arial" --size 25

  10) Embed subtitle into video with primary color red and outline color blue
  avsub "input.mp4" - -e "input.srt" --color1 red --color2 blue

NOTES
  1) Valid Characters for File Extensions
  abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

  2) Privileged Access
  AVsub forbids privileged access by default.

  3) No Files to Process with Current Options
  Clearing the cache information may resolve this situation.

ISSUES
  1) Pathname with Bad Characters #1 [wontfix]
  A pathname containing bad characters may cause the operation to fail.

ABOUT
  This tool is for basic operations, use FFmpeg for advanced operations.
  See https://github.com/serhatcelik/avsub for more information.
"""

from __future__ import absolute_import

from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
from typing import List

from avsub import OS
from avsub.core import consts
from avsub.core import notice_
from avsub.core.tools import clear_cache
from avsub.core.tools import convert_trim
from avsub.core.tools import is_user_an_admin
from avsub.core.tools import shutdown_cancel
from avsub.str import Str


def create_parser() -> ArgumentParser:
    """Create a parser to parse command-line arguments."""
    parser: ArgumentParser = ArgumentParser(
        prog="avsub",
        usage="%(prog)s [<input> <extension> [<extra_option> ...]]",
        description=f"AVsub — A simplified command-line interface for FFmpeg\n"
                    f"Created by {notice_.AUTHOR} "
                    f"(with the help of my family and a friend)",
        epilog=__doc__, formatter_class=RawTextHelpFormatter,
        prefix_chars="+-", allow_abbrev=False,  # avsub: C2500
    )

    group_hardsub = parser.add_argument_group("hardsub arguments")
    group_independent = parser.add_argument_group("independent arguments")

    mutual_group_0 = parser.add_mutually_exclusive_group()
    mutual_group_1 = group_independent.add_mutually_exclusive_group()

    ########################
    # Positional Arguments #
    ########################
    parser.add_argument(
        "input", metavar="input", action="store",
        help="input file or folder, see examples 1-2",
    )
    parser.add_argument(
        "ext", metavar="extension", action="store",
        help="output extension, '-' to keep input extension, see example 3",
    )

    ######################
    # Optional Arguments #
    ######################
    parser.add_argument(
        "+a", metavar="<codec>", dest="acodec", action="store", default=None,
        help="set %(metavar)s as output audio codec, see example 4",
    )
    mutual_group_0.add_argument(
        "-A", "--audio", dest="oaudio", action="store_const", default=[],
        const=["-vn", "-sn", "-dn"],
        help="choose audio stream only, see example 5",
    )
    parser.add_argument(
        "--channel", metavar="<channel>", dest="ac", action="store",
        default=None, choices=consts.AC,
        help="set %(metavar)s as output audio channel;\n"
             "\tCHOICES: %(choices)s".expandtabs(2),
    )
    parser.add_argument(
        "-C", "--compress", metavar="<value>", dest="crf", action="store",
        nargs="?", default=None, const=30, type=int, choices=consts.CRF,
        help=f"set %(metavar)s as crf value for compression, see example 6;\n"
             f"\tCONSTANT: %(const)s\n"
             f"\tCHOICES: {consts.CRF[0]}-{consts.CRF[-1]}".expandtabs(2),
    )
    parser.add_argument(
        "-c", "--copy", metavar="<stream>", dest="copy", action="store",
        nargs="+", default=[], choices=["audio", "video", "sub", "all"],
        help="use copy codec for output %(metavar)s, see example 3;\n"
             "\tCHOICES: %(choices)s".expandtabs(2),
    )
    parser.add_argument(
        "-f", metavar="<args>", dest="custom_ffmpeg", action="store",
        default=None,
        help="provide %(metavar)s as an ffmpeg argument list, be careful!",
    )
    parser.add_argument(
        "--no-map-all", dest="no_map_all", action="store_true", default=False,
        help="do not choose all streams, may cause data loss!",
    )
    parser.add_argument(
        "--remove", metavar="<stream>", dest="remove", action="store",
        nargs="+", default=[],
        choices=["audio", "video", "sub", "data", "metadata", "chapters"],
        help="do not copy %(metavar)s from input to output, see example 7;\n"
             "\tCHOICES: %(choices)s".expandtabs(2),
    )  # avsub: N2202
    parser.add_argument(
        "+s", metavar="<codec>", dest="scodec", action="store", default=None,
        help="set %(metavar)s as output subtitle codec",
    )
    parser.add_argument(
        "--speed", metavar="<preset>", dest="preset", action="store",
        nargs="?", default=None, const="fast",
        choices=["faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="set %(metavar)s as video encoding speed;\n"
             "\tCONSTANT: %(const)s\n"
             "\tCHOICES: %(choices)s".expandtabs(2),
    )  # avsub: N2001,C2000
    mutual_group_0.add_argument(
        "-S", "--subtitle", dest="osubtitle", action="store_const", default=[],
        const=["-an", "-vn", "-dn"], help="choose subtitle stream only",
    )
    parser.add_argument(
        "--trim", metavar=("<from>", "<to>"), dest="trim", action="store",
        nargs=2, default=None,
        help="extract a part of input from <from> to <to>, see example 8",
    )
    parser.add_argument(
        "+v", metavar="<codec>", dest="vcodec", action="store", default=None,
        help="set %(metavar)s as output video codec, see example 4",
    )
    mutual_group_0.add_argument(
        "-V", "--video", dest="ovideo", action="store_const", default=[],
        const=["-an", "-sn", "-dn"], help="choose video stream only",
    )

    #####################
    # Hardsub Arguments #
    #####################
    group_hardsub.add_argument(
        "-b", "--box", dest="box", action="store_const", default=None,
        const="3", help="add an opaque box around subtitle",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--color1", metavar="<color>", dest="c1", action="store", default=None,
        choices=consts.C1,
        help="set %(metavar)s as subtitle primary color, see example 10",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--color2", metavar="<color>", dest="c2", action="store", default=None,
        choices=consts.C2,
        help="set %(metavar)s as subtitle outline color, see example 10",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "-e", "--embed", metavar="<subtitle>", dest="embed", action="store",
        default=None,
        help="embed %(metavar)s into video (hardsub), see example 9",
    )
    group_hardsub.add_argument(
        "--font", metavar="<name>", dest="font", action="store", default=None,
        help="set %(metavar)s as subtitle font name, see example 9",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--position", metavar="<position>", dest="align", action="store",
        default=None, choices=consts.ALIGN,
        help="set %(metavar)s as subtitle alignment",
    )  # avsub: C2003
    group_hardsub.add_argument(
        "--size", metavar="<value>", dest="size", action="store", default=None,
        type=int, help="set %(metavar)s as subtitle font size, see example 9",
    )  # avsub: C2003

    #########################
    # Independent Arguments #
    #########################
    group_independent.add_argument(
        "-B", "--bypass", dest="bypass", action="store_true", default=False,
        help="ignore warnings, not recommended!",
    )
    group_independent.add_argument(
        "--clear-cache", dest="clear_cache", action="version", default=None,
        version=clear_cache(),
        help="clear cache info for successfully completed files, see note 3",
    )  # avsub: N2302
    mutual_group_1.add_argument(
        "--exclude", metavar="<extension>", dest="exclude", action="store",
        nargs="+", default=[],
        help="do not process input if its extension is %(metavar)s",
    )
    group_independent.add_argument(
        "-F", "--ffmpeg", dest="show_ffmpeg", action="store_true",
        default=False, help="show the ffmpeg command during processing",
    )
    group_independent.add_argument(
        "--fix-startup", dest="fix_startup", action="store_true",
        default=False, help="repair startup program that checks for updates",
    )  # avsub: N2500
    group_independent.add_argument(
        "-H", "--hidden", dest="hidden", action="store_true", default=False,
        help="include hidden/protected input, see example 2",
    )
    group_independent.add_argument(
        "-i", "--inform", dest="loglevel", action="count", default=0,
        help=f"show more info, can be used up to {len(consts.LOGLEVEL)} times",
    )
    group_independent.add_argument(
        "-L", "--license", dest="license", action="version", default=None,
        version=notice_.__doc__, help="show copyright notice and exit",
    )
    group_independent.add_argument(
        "-l", "--log", dest="log", action="store_true", default=False,
        help="log results to a file inside the parent of the output folder",
    )  # avsub: N2101
    group_independent.add_argument(
        "--no-err-exit", dest="no_err_exit", action="store_true",
        default=False, help="continue when fatal ffmpeg error is encountered",
    )  # avsub: N2200
    group_independent.add_argument(
        "--no-open-dir", metavar="<mode>", dest="no_open_dir", action="store",
        nargs="?", default="empty" if OS.nt else "always", const="always",
        choices=["never", "empty", "always"],
        help="set %(metavar)s to change the output folder opening behavior;\n"
             "\tDEFAULT: %(default)s\n"
             "\tCONSTANT: %(const)s\n"
             "\tCHOICES: %(choices)s".expandtabs(2),
    )  # avsub: C2001,C2002,C2010
    mutual_group_1.add_argument(
        "--only", metavar="<extension>", dest="only", action="store",
        nargs="+", default=[],
        help="process input only if its extension is %(metavar)s",
    )
    group_independent.add_argument(
        "-o", "--output", metavar="<folder>", dest="temp", action="store",
        default=consts.DIR_THE_TEMP_DEF,
        help="set %(metavar)s as the parent of the output folder",
    )  # avsub: N2100
    group_independent.add_argument(
        "--shutdown", metavar="<timeout>", dest="shut", action="store",
        nargs="?", default=None, const=consts.SHUT[0], type=int,
        choices=consts.SHUT,
        help=f"shut down the computer after %(metavar)s minutes when done;\n"
             f"\tCONSTANT: %(const)s\n"
             f"\tCHOICES: {consts.SHUT[0]}-{consts.SHUT[-1]}".expandtabs(2),
    )  # avsub: N2600
    group_independent.add_argument(
        "--shutdown-cancel", dest="shut_cancel", action="version",
        default=None, version=shutdown_cancel(),
        help="cancel a pending shutdown",
    )  # avsub: N2601
    group_independent.add_argument(
        "--use-cache", dest="use_cache", action="store_true", default=False,
        help="use cache info to process only unsuccessful files",
    )  # avsub: N2301
    group_independent.add_argument(
        "-v", "--version", dest="version", action="version", default=None,
        version=notice_.VERSION, help="show program version and exit",
    )

    return parser


def check_opts(opts: Namespace) -> List[list]:
    """Check for parsed command-line arguments."""
    return [
        [
            all([Str(opts.input).iscwd() and opts.input != ".",
                 all(_ not in opts.input for _ in ["/", "\\"])]),
            f"input ~ '{opts.input}': This is current folder, use '.'",
            "!",
        ],
        [
            all([Str(opts.temp).iscwd() and opts.temp != ".",
                 all(_ not in opts.temp for _ in ["/", "\\"])]),
            f"-o/--output ~ '{opts.temp}': This is current folder, use '.'",
            "!",
        ],
        [
            not Str(opts.input).exists(),
            f"input ~ '{opts.input}': No such file or folder",
            "!",
        ],
        [
            all([Str(opts.temp).abs() != Str(consts.DIR_THE_TEMP_DEF).abs(),
                 not Str(opts.temp).isdir()]),
            f"-o/--output ~ '{opts.temp}': No such folder",
            "!",
        ],  # avsub: C2231,F2240
        [
            not Str(opts.ext).isext(),
            f"extension ~ '{opts.ext}': Contains invalid chars, see note 1",
            "!",
        ],
        [
            any(not Str(ext).isext() for ext in opts.exclude),
            "extension: BAN: --exclude: Contains bad extensions, see note 1",
            "!",
        ],
        [
            any(not Str(ext).isext() for ext in opts.only),
            "extension: BAN: --only: Contains bad extensions, see note 1",
            "!",
        ],
        [
            opts.embed and not Str(opts.embed).isfile(),
            f"-e/--embed ~ '{opts.embed}': No such file",
            "!",
        ],
        [
            opts.embed and Str(opts.input).isdir(),
            f"-e/--embed: BAN: input ~ '{opts.input}': This is a folder",
            "!",
        ],
        [
            not opts.hidden and Str(opts.input).ishidden(),
            f"-H/--hidden: BAN: input ~ '{opts.input}': Protected X",
            "!",
        ],
        [
            not opts.hidden and opts.embed and Str(opts.embed).ishidden(),
            f"-H/--hidden: BAN: -e/--embed ~ '{opts.embed}': Protected X",
            "!",
        ],
        [
            not opts.hidden and Str(opts.temp).ishidden(),
            f"-H/--hidden: BAN: -o/--output ~ '{opts.temp}': Protected X",
            "!",
        ],
        [
            is_user_an_admin(),
            "Privileged access detected, exiting by default, see note 2",
            "W",
        ],  # avsub: C2202
        [
            opts.embed and ("video" in opts.copy or "all" in opts.copy),
            "-e/--embed: BAN: -c/--copy {video | all}: Forbidden option",
            "W",
        ],
        [
            opts.embed and opts.vcodec == "copy",
            "-e/--embed: BAN: +v copy: Forbidden option",
            "W",
        ],
        [
            opts.ac and ("audio" in opts.copy or "all" in opts.copy),
            "--channel: BAN: -c/--copy {audio | all}: Meaningless option",
            "W",
        ],
        [
            opts.ac and opts.acodec == "copy",
            "--channel: BAN: +a copy: Meaningless option",
            "W",
        ],
        [
            opts.oaudio and "audio" in opts.remove,
            "-A/--audio: BAN: --remove audio: Mutually exclusive group",
            "W",
        ],
        [
            opts.ovideo and "video" in opts.remove,
            "-V/--video: BAN: --remove video: Mutually exclusive group",
            "W",
        ],
        [
            opts.osubtitle and "sub" in opts.remove,
            "-S/--subtitle: BAN: --remove sub: Mutually exclusive group",
            "W",
        ],
        [
            sum(1 for _ in ["audio", "video", "sub"] if _ in opts.remove) == 3,
            "--remove audio video sub: Output contains no stream",
            "W",
        ],
        [
            all([bool(opts.acodec) and opts.acodec != "copy",
                 any(stream in opts.copy for stream in ["audio", "all"])]),
            "+a: BAN: -c/--copy {audio | all}: Mutually exclusive group",
            "W",
        ],
        [
            all([bool(opts.vcodec) and opts.vcodec != "copy",
                 any(stream in opts.copy for stream in ["video", "all"])]),
            "+v: BAN: -c/--copy {video | all}: Mutually exclusive group",
            "W",
        ],
        [
            all([bool(opts.scodec) and opts.scodec != "copy",
                 any(stream in opts.copy for stream in ["sub", "all"])]),
            "+s: BAN: -c/--copy {sub | all}: Mutually exclusive group",
            "W",
        ],
        [
            opts.trim and convert_trim() == "smaller",
            "--trim: <to> value (2nd) smaller than or equal to <from> value",
            "W",
        ],
        [
            opts.trim and convert_trim() == "syntax",
            "--trim: Must be in HH:MM:SS or SS syntax, see example 8",
            "W",
        ],
        [
            opts.trim and ("video" in opts.copy or "all" in opts.copy),
            "--trim: BAN: -c/--copy {video | all}: Meaningless option",
            "W",
        ],
        [
            opts.trim and opts.vcodec == "copy",
            "--trim: BAN: +v copy: Meaningless option",
            "W",
        ],
    ]
