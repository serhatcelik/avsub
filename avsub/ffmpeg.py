# coding=utf-8

# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This module provides ways to use FFmpeg effectively.
"""

import inspect
import os
import subprocess
from subprocess import CalledProcessError
from subprocess import TimeoutExpired

from avsub.core import consts
from avsub.core import x
from avsub.core.tools import mark_as_hidden
from avsub.str import Str


class FFmpeg:
    cmd = ["ffmpeg", "-n", "-hide_banner", "-stats"]
    _force_style = []

    def _add_map_all_to_cmd___(self):
        self.cmd += ["-map", "0"] if not x.OPTS.no_map_all else []

    def _add_loglevel_to_cmd___(self):
        self.cmd += ["-loglevel", str(consts.LOGLEVEL[x.OPTS.loglevel])]

    def _add_preset_to_cmd___(self):
        self.cmd += ["-preset", x.OPTS.preset] if x.OPTS.preset else []

    def _add_crf_to_cmd___(self):
        self.cmd += [
            "-crf", str(x.OPTS.crf)
        ] if isinstance(x.OPTS.crf, int) else []

    def _add_ac_to_cmd___(self):
        self.cmd += ["-ac", consts.AC[x.OPTS.ac]] if x.OPTS.ac else []

    def _add_remove_audio_to_cmd___(self):
        self.cmd += [
            "-an",
        ] if all(["audio" in x.OPTS.remove, "-an" not in self.cmd]) else []

    def _add_remove_video_to_cmd___(self):
        self.cmd += [
            "-vn",
        ] if all(["video" in x.OPTS.remove, "-vn" not in self.cmd]) else []

    def _add_remove_subtitle_to_cmd___(self):
        self.cmd += [
            "-sn",
        ] if all(["sub" in x.OPTS.remove, "-sn" not in self.cmd]) else []

    def _add_remove_metadata_to_cmd___(self):
        self.cmd += "-map_metadata", str(-abs("metadata" in x.OPTS.remove))

    def _add_remove_chapters_to_cmd___(self):
        self.cmd += "-map_chapters", str(-abs("chapters" in x.OPTS.remove))

    def _add_only_audio_to_cmd___(self):
        self.cmd += [_ for _ in x.OPTS.oaudio if _ not in self.cmd]

    def _add_only_video_to_cmd___(self):
        self.cmd += [_ for _ in x.OPTS.ovideo if _ not in self.cmd]

    def _add_only_subtitle_to_cmd___(self):
        self.cmd += [_ for _ in x.OPTS.osubtitle if _ not in self.cmd]

    def _add_copy_audio_to_cmd___(self):
        self.cmd += ["-acodec", "copy"] if "audio" in x.OPTS.copy else []

    def _add_copy_video_to_cmd___(self):
        self.cmd += ["-vcodec", "copy"] if "video" in x.OPTS.copy else []

    def _add_copy_subtitle_to_cmd___(self):
        self.cmd += ["-scodec", "copy"] if "sub" in x.OPTS.copy else []

    def _add_copy_all_to_cmd___(self):
        self.cmd += ["-codec", "copy"] if "all" in x.OPTS.copy else []

    def _add_codec_audio_to_cmd___(self):
        self.cmd += ["-acodec", x.OPTS.acodec] if x.OPTS.acodec else []

    def _add_codec_video_to_cmd___(self):
        self.cmd += ["-vcodec", x.OPTS.vcodec] if x.OPTS.vcodec else []

    def _add_codec_subtitle_to_cmd___(self):
        self.cmd += ["-scodec", x.OPTS.scodec] if x.OPTS.scodec else []

    def _add_trim_to_cmd___(self):
        self.cmd += [
            "-ss", str(x.OPTS.trim[0]),
            "-to", str(x.OPTS.trim[-1]),
        ] if x.OPTS.trim else []

    def _add_fontname_to_force_style___(self):
        self._force_style += [
            "FontName=%s" % x.OPTS.FontName,
        ] if x.OPTS.FontName else []

    def _add_fontsize_to_force_style___(self):
        # Note: abs() is used to prevent "Assertion failed" error from FFmpeg
        self._force_style += [
            "FontSize=%s" % abs(x.OPTS.FontSize),
        ] if x.OPTS.FontSize else []

    def _add_alignment_to_force_style___(self):
        self._force_style += [
            "Alignment=%s" % consts.ALIGNMENT[x.OPTS.Alignment],
        ] if x.OPTS.Alignment else []

    def _add_borderstyle_to_force_style___(self):
        self._force_style += [
            "BorderStyle=%s" % x.OPTS.BorderStyle,
        ] if x.OPTS.BorderStyle else []

    def _add_primarycolour_to_force_style___(self):
        self._force_style += [
            "PrimaryColour=%s" % consts.PRIMARYCOLOUR[x.OPTS.PrimaryColour],
        ] if x.OPTS.PrimaryColour else []

    def _add_outlinecolour_to_force_style___(self):
        self._force_style += [
            "OutlineColour=%s" % consts.OUTLINECOLOUR[x.OPTS.OutlineColour],
        ] if x.OPTS.OutlineColour else []

    def build(self):
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0].endswith("___"):
                member[-1]()  # Call the method of the FFmpeg class

        if x.OPTS.custom_ffmpeg:
            self.cmd += x.OPTS.custom_ffmpeg.strip().split()
        x.CMD_TO_SHOW = " ".join(self.cmd)

    def build_hardsub(self, subpath):
        filter_v = "subtitles=%s" % subpath

        if self._force_style:
            filter_v += ":force_style='%s'" % ",".join(self._force_style)

        x.CMD_TO_SHOW = "%s -filter:v \"%s\"" % (" ".join(self.cmd), filter_v)
        self.cmd += ["-filter:v", filter_v]


def check():
    try:
        subprocess.check_call(["ffmpeg", "-version"],
                              timeout=4,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except (FileNotFoundError, CalledProcessError, TimeoutExpired):
        return False
    return True


def execute(cmd, files):
    for i, file in enumerate(files):
        # Note: Output base name is the same as input base name
        output = x.NOT_PROCESSED[file]

        # If the output is already in the destination folder...
        if Str(output).exists():
            # Note: Also for inputs with the same name but different extensions
            x.RUN_FFMPEG = False
        else:
            x.RUN_FFMPEG = True
            if x.RUN:  # avsub: F2001
                # Note: Output is no longer marked as "not processed"
                x.NOT_PROCESSED.pop(file)
                x.DEL_ON_EXIT.update({file: output})

        if x.RUN:  # avsub: F2002
            print("[*] Running [%*d/%d]: '%s' -> %s" % (len(str(len(files))),
                                                        i + 1, len(files),
                                                        Str(file).base(),
                                                        Str(file).extout()))
            if x.OPTS.show_ffmpeg:
                line = "~" * os.get_terminal_size().columns
                print(line)
                print("%s \"%s\" -i \"%s\"" % (x.CMD_TO_SHOW, output, file))
                print(line)

        new_cmd = cmd + [output, "-i", file]

        try:
            # If an exit signal has already been caught...
            if not x.RUN:
                return
            if not x.RUN_FFMPEG:  # avsub: F2000
                print("File '%s' already exists, passing" % output)
                continue
            # Note: Disable "Press [q] to stop" feature with "DEVNULL"
            subprocess.run(new_cmd, check=True, stdin=subprocess.DEVNULL)
        except CalledProcessError:
            # Note: Output will be deleted on exit
            continue
        except FileNotFoundError:
            x.FATAL_FFMPEG = file
            print("FFmpeg could not be executed (fatal)")
            return
        else:
            # Note: Output will not be deleted on exit
            x.SUCCEEDED.update({file: x.DEL_ON_EXIT.pop(file)})
            if Str(file).ishidden():
                mark_as_hidden(output)  # avsub: N2000
