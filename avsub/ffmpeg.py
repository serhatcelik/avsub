# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This module provides ways to use FFmpeg effectively."""

# pylint: disable=consider-using-f-string

from __future__ import absolute_import

import inspect
from subprocess import CalledProcessError  # nosec
from typing import List

from avsub.core import consts
from avsub.core import x
from avsub.core.tools import avsubprocess
from avsub.core.tools import convert_trim
from avsub.core.tools import create_progress
from avsub.core.tools import mark_as_hidden
from avsub.core.tools import repeater
from avsub.core.tools import save_to_cache_as_done
from avsub.str import Str


class FFmpeg:
    """Base class for FFmpeg."""

    cmd: List[str] = ["ffmpeg", "-n", "-hide_banner", "-stats"]
    _f_style: List[str] = []

    def _add_map_all_to_cmd___(self) -> None:
        self.cmd += ["-map", "0"] if not x.OPTS.no_map_all else []

    def _add_loglevel_to_cmd___(self) -> None:
        self.cmd += ["-loglevel", str(consts.LOGLEVEL[x.OPTS.loglevel])]

    def _add_preset_to_cmd___(self) -> None:
        self.cmd += ["-preset", x.OPTS.preset] if x.OPTS.preset else []

    def _add_crf_to_cmd___(self) -> None:
        self.cmd += ["-crf", str(x.OPTS.crf)] if x.OPTS.crf is not None else []

    def _add_ac_to_cmd___(self) -> None:
        self.cmd += ["-ac", str(consts.AC[x.OPTS.ac])] if x.OPTS.ac else []

    def _add_remove_audio_to_cmd___(self) -> None:
        if "audio" in x.OPTS.remove:
            self.cmd += ["-an"] if "-an" not in self.cmd else []

    def _add_remove_video_to_cmd___(self) -> None:
        if "video" in x.OPTS.remove:
            self.cmd += ["-vn"] if "-vn" not in self.cmd else []

    def _add_remove_subtitle_to_cmd___(self) -> None:
        if "sub" in x.OPTS.remove:
            self.cmd += ["-sn"] if "-sn" not in self.cmd else []

    def _add_remove_data_to_cmd___(self) -> None:
        if "data" in x.OPTS.remove:
            self.cmd += ["-dn"] if "-dn" not in self.cmd else []

    def _add_remove_metadata_to_cmd___(self) -> None:
        self.cmd += "-map_metadata", str(-abs("metadata" in x.OPTS.remove))

    def _add_remove_chapters_to_cmd___(self) -> None:
        self.cmd += "-map_chapters", str(-abs("chapters" in x.OPTS.remove))

    def _add_only_audio_to_cmd___(self) -> None:
        self.cmd += [_ for _ in x.OPTS.oaudio if _ not in self.cmd]

    def _add_only_video_to_cmd___(self) -> None:
        self.cmd += [_ for _ in x.OPTS.ovideo if _ not in self.cmd]

    def _add_only_subtitle_to_cmd___(self) -> None:
        self.cmd += [_ for _ in x.OPTS.osubtitle if _ not in self.cmd]

    def _add_copy_audio_to_cmd___(self) -> None:
        self.cmd += ["-acodec", "copy"] if "audio" in x.OPTS.copy else []

    def _add_copy_video_to_cmd___(self) -> None:
        self.cmd += ["-vcodec", "copy"] if "video" in x.OPTS.copy else []

    def _add_copy_subtitle_to_cmd___(self) -> None:
        self.cmd += ["-scodec", "copy"] if "sub" in x.OPTS.copy else []

    def _add_copy_all_to_cmd___(self) -> None:
        self.cmd += ["-codec", "copy"] if "all" in x.OPTS.copy else []

    def _add_codec_audio_to_cmd___(self) -> None:
        self.cmd += ["-acodec", x.OPTS.acodec] if x.OPTS.acodec else []

    def _add_codec_video_to_cmd___(self) -> None:
        self.cmd += ["-vcodec", x.OPTS.vcodec] if x.OPTS.vcodec else []

    def _add_codec_subtitle_to_cmd___(self) -> None:
        self.cmd += ["-scodec", x.OPTS.scodec] if x.OPTS.scodec else []

    def _add_trim_to_cmd___(self) -> None:
        if x.OPTS.trim is not None:
            first: str = convert_trim()[0]
            last: str = convert_trim()[-1]
            self.cmd += ["-ss", first, "-to", last]

    def _add_fontname_to_force_style___(self) -> None:
        self._f_style += [f"FontName={x.OPTS.font}"] if x.OPTS.font else []

    def _add_fontsize_to_force_style___(self) -> None:
        if x.OPTS.size is not None:  # avsub: F2201
            # Note: Used abs() to prevent "Assertion failed" error from FFmpeg
            self._f_style += [f"FontSize={abs(x.OPTS.size)}"]

    def _add_alignment_to_force_style___(self) -> None:
        if x.OPTS.align is not None:
            self._f_style += [f"Alignment={str(consts.ALIGN[x.OPTS.align])}"]

    def _add_borderstyle_to_force_style___(self) -> None:
        self._f_style += [f"BorderStyle={x.OPTS.box}"] if x.OPTS.box else []

    def _add_primarycolour_to_force_style___(self) -> None:
        if x.OPTS.c1 is not None:
            self._f_style += [f"PrimaryColour={consts.C1[x.OPTS.c1]}"]

    def _add_outlinecolour_to_force_style___(self) -> None:
        if x.OPTS.c2 is not None:
            self._f_style += [f"OutlineColour={consts.C2[x.OPTS.c2]}"]

    def build(self) -> None:
        """Update the ultimate FFmpeg command."""
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0].endswith("___"):
                member[-1]()  # Call the method of the FFmpeg class

        if x.OPTS.custom_ffmpeg:
            self.cmd += x.OPTS.custom_ffmpeg.strip().split()
        x.CMD_TO_SHOW = " ".join(self.cmd)

    def build_hardsub(self, subpath: str) -> None:
        """Update the ultimate FFmpeg command for hardsub operation."""
        filter_v: str = f"subtitles=filename={subpath}"

        if self._f_style:
            filter_v += ":force_style='%s'" % ",".join(self._f_style)

        x.CMD_TO_SHOW = "%s -filter:v \"%s\"" % (" ".join(self.cmd), filter_v)
        self.cmd += ["-filter:v", filter_v]


@repeater(retry=2, countdown=3)  # avsub: C2201
def check() -> bool:
    """Start a run test for FFmpeg."""
    avsubprocess(["ffmpeg", "-version"], call=True, timeout=8)
    return True


def execute(cmd: List[str], files: List[str]) -> None:
    """Finish creating the ultimate FFmpeg command and execute it."""
    for i, file in enumerate(files):
        # Note: Output base name is the same as input base name
        output: str = x.NOT_PROCESSED[file]

        # If the output is already in the destination folder...
        if Str(output).exists():
            # Note: Also for inputs with the same name but different extensions
            x.RUN_FFMPEG = False
        else:
            x.RUN_FFMPEG = True
            if x.RUN:  # avsub: F2001
                # Note: Output is no longer marked as "not processed"
                x.DEL_ON_EXIT.update({file: x.NOT_PROCESSED.pop(file)})

        if x.RUN:  # avsub: F2002
            pbar: str = create_progress(i, total=files)
            base: str = Str(file).base()
            extout: str = Str(file).extout()
            print("[*] Running", f"{pbar}: '{base}' -> {extout}")
            print("[*] Press Ctrl+C to stop")
            if x.OPTS.show_ffmpeg:
                line: str = Str("~").line()
                print(line)
                print(f"{x.CMD_TO_SHOW} \"{output}\" -i \"{file}\"")
                print(line)

        try:
            # If an exit signal has already been caught...
            if not x.RUN:
                return
            if not x.RUN_FFMPEG:  # avsub: F2000
                print(f"File '{output}' already exists, passing")
                continue
            avsubprocess(cmd + [output, "-i", file])
        except CalledProcessError:
            # Note: Output will be deleted on exit
            continue
        except FileNotFoundError:
            x.FATAL_FFMPEG.update({file: x.DEL_ON_EXIT[file]})
            print("FFmpeg could not be executed (fatal)")
            if not x.OPTS.no_err_exit:
                return
            continue

        # Note: Output will not be deleted on exit
        x.SUCCEEDED.update({file: x.DEL_ON_EXIT.pop(file)})
        if Str(file).ishidden():
            mark_as_hidden(output)  # avsub: N2000
        save_to_cache_as_done(file)  # avsub: N2300
