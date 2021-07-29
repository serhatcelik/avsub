# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This module provides ways to use FFmpeg effectively.
"""

import inspect
import os
import string
import subprocess

from avsub import core


class FFmpeg:
    cmd = ["ffmpeg", "-n", "-hide_banner", "-stats"]
    force_style = string.Template("FontName=$FontName,"
                                  "FontSize=$FontSize,"
                                  "Alignment=$Alignment,"
                                  "BorderStyle=$BorderStyle,"
                                  "PrimaryColour=$PrimaryColour,"
                                  "OutlineColour=$OutlineColour,")

    def __init__(self, parsed_args):
        self.opts = parsed_args

    def __str__(self):
        return " ".join(self.cmd)

    def _add_map_all_to_cmd___(self):
        self.cmd += ["-map", "0"] if not self.opts.no_map_all else []

    def _add_loglevel_to_cmd___(self):
        self.cmd += ["-loglevel", core.LOGLEVELS[self.opts.loglevel]]

    def _add_preset_to_cmd___(self):
        self.cmd += ["-preset", self.opts.preset] if self.opts.preset else []

    def _add_crf_to_cmd___(self):
        self.cmd += [
            "-crf", str(self.opts.crf)
        ] if isinstance(self.opts.crf, int) else []  # avsub: F1202

    def _add_ac_to_cmd___(self):
        self.cmd += ["-ac", core.ACS[self.opts.ac]] if self.opts.ac else []

    def _add_remove_audio_to_cmd___(self):
        self.cmd += ["-an"] if "audio" in self.opts.remove else []

    def _add_remove_video_to_cmd___(self):
        self.cmd += ["-vn"] if "video" in self.opts.remove else []

    def _add_remove_subtitle_to_cmd___(self):
        self.cmd += ["-sn"] if "sub" in self.opts.remove else []

    def _add_remove_metadata_to_cmd___(self):
        self.cmd += "-map_metadata", str(-abs("metadata" in self.opts.remove))

    def _add_remove_chapters_to_cmd___(self):
        self.cmd += "-map_chapters", str(-abs("chapters" in self.opts.remove))

    def _add_only_audio_to_cmd___(self):
        self.cmd += [_ for _ in self.opts.oaudio if _ not in self.cmd]

    def _add_only_video_to_cmd___(self):
        self.cmd += [_ for _ in self.opts.ovideo if _ not in self.cmd]

    def _add_only_subtitle_to_cmd___(self):
        self.cmd += [_ for _ in self.opts.osubtitle if _ not in self.cmd]

    def _add_copy_audio_to_cmd___(self):
        self.cmd += ["-acodec", "copy"] if "audio" in self.opts.copy else []

    def _add_copy_video_to_cmd___(self):
        self.cmd += ["-vcodec", "copy"] if "video" in self.opts.copy else []

    def _add_copy_subtitle_to_cmd___(self):
        self.cmd += ["-scodec", "copy"] if "sub" in self.opts.copy else []

    def _add_copy_all_to_cmd___(self):
        self.cmd += ["-codec", "copy"] if "all" in self.opts.copy else []

    def _add_codec_audio_to_cmd___(self):
        self.cmd += ["-acodec", self.opts.acodec] if self.opts.acodec else []

    def _add_codec_video_to_cmd___(self):
        self.cmd += ["-vcodec", self.opts.vcodec] if self.opts.vcodec else []

    def _add_codec_subtitle_to_cmd___(self):
        self.cmd += ["-scodec", self.opts.scodec] if self.opts.scodec else []

    def _add_trim_to_cmd___(self):
        self.cmd += [
            "-ss", str(self.opts.trim[0]),
            "-to", str(self.opts.trim[-1]),
        ] if self.opts.trim else []

    def _add_fontname_to_force_style___(self):
        _ = {"FontName": self.opts.FontName}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_fontsize_to_force_style___(self):
        # Note: "abs" is used to prevent "Assertion failed" error from FFmpeg
        _ = {"FontSize": abs(self.opts.FontSize)}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_alignment_to_force_style___(self):
        _ = {"Alignment": core.ALIGNMENTS[self.opts.Alignment]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_borderstyle_to_force_style___(self):
        _ = {"BorderStyle": self.opts.BorderStyle}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_primarycolour_to_force_style___(self):
        _ = {"PrimaryColour": core.COLORS[self.opts.PrimaryColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_outlinecolour_to_force_style___(self):
        _ = {"OutlineColour": core.COLORS[self.opts.OutlineColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def build(self):
        """
        Update the ultimate FFmpeg command.
        """

        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0].endswith("___"):
                member[-1]()  # Call the method of the FFmpeg class

        self.cmd += self.opts.custom_ffmpeg.strip().split()
        core.CMD_TO_SHOW = self.__str__()

    def build_force_style(self, subpath):
        """
        Update the ultimate FFmpeg command for the hardsub operation.

        :param subpath: Subtitle pathname.
        """

        force_style = self.force_style.template
        filter_v = "subtitles=%s:force_style='%s'" % (subpath, force_style)

        core.CMD_TO_SHOW = "%s -filter:v \"%s\"" % (self.__str__(), filter_v)
        self.cmd += ["-filter:v", filter_v]


def execute(cmd, files):
    """
    Finish creating the ultimate FFmpeg command and execute it.

    :param cmd: FFmpeg command to finish creating.
    :param files: All files to process.
    """

    for i, file in enumerate(files):
        # Note: Output base name is the same as input base name
        output = core.NOT_PROCESSED[file]

        # If the output is already in the destination folder...
        if core.path_exists(output):
            # Note: Also for inputs with the same name but different extensions
            pass
        else:
            # Store as {input: output} to delete the output on exit
            core.DEL_ON_EXIT.update({file: output})
            if file in core.NOT_PROCESSED:
                # Note: Output is no longer marked as "not processed"
                core.NOT_PROCESSED.pop(file)

        # Note: Convert "int" to "str" to find the length of the precision
        print("[*] Running [%*d/%d]: '%s' -> %s" % (len(str(len(files))),
                                                    i + 1, len(files),
                                                    core.basename(file),
                                                    core.get_ext(file)))
        if core.OPTS.show_ffmpeg:  # avsub: C1300
            columns = os.get_terminal_size().columns
            print("-" * columns)
            print("%s \"%s\" -i \"%s\"" % (core.CMD_TO_SHOW, output, file))
            print("-" * columns)

        # Finish creating the ultimate FFmpeg command once
        new_cmd = cmd + [output, "-i", file]
        try:
            # If an exit signal has already been caught...
            if not core.RUN:
                return
            # Note: Disable "Press [q] to stop" feature with "DEVNULL"
            subprocess.run(new_cmd, check=True, stdin=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Note: Output will be deleted on exit
            pass
        except FileNotFoundError:
            core.FATAL_FFMPEG = core.basename(file)
            print("[!] FFmpeg could not be executed (fatal)")
            return
        else:
            if file in core.DEL_ON_EXIT:
                core.DEL_ON_EXIT.pop(file)  # Pop output to not delete on exit
