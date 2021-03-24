# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import string
import inspect
import subprocess
from avsub import core


class FFmpeg:
    cmd = ["ffmpeg", "-n", "-hide_banner", "-stats", "-map", "0"]
    force_style = string.Template("FontName=$FontName,"
                                  "FontSize=$FontSize,"
                                  "Alignment=$Alignment,"
                                  "BorderStyle=$BorderStyle,"
                                  "PrimaryColour=$PrimaryColour,"
                                  "OutlineColour=$OutlineColour,")

    def __init__(self, opts):
        self.opts = opts

    def _add_loglevel_to_cmd(self):
        self.cmd += ["-loglevel", self.opts.loglevel]

    def _add_preset_to_cmd(self):
        self.cmd += ["-preset", self.opts.preset] if self.opts.preset else []

    def _add_crf_to_cmd(self):
        self.cmd += ["-crf", str(self.opts.crf)] if self.opts.crf else []

    def _add_remove_audio_to_cmd(self):
        self.cmd += ["-an"] if "audio" in self.opts.remove else []

    def _add_remove_video_to_cmd(self):
        self.cmd += ["-vn"] if "video" in self.opts.remove else []

    def _add_remove_subtitle_to_cmd(self):
        self.cmd += ["-sn"] if "sub" in self.opts.remove else []

    def _add_remove_metadata_to_cmd(self):
        self.cmd += "-map_metadata", str(-abs("metadata" in self.opts.remove))

    def _add_remove_chapters_to_cmd(self):
        self.cmd += "-map_chapters", str(-abs("chapters" in self.opts.remove))

    def _add_only_audio_to_cmd(self):
        self.cmd += [i for i in self.opts.oaudio if i not in self.cmd]

    def _add_only_video_to_cmd(self):
        self.cmd += [i for i in self.opts.ovideo if i not in self.cmd]

    def _add_only_subtitle_to_cmd(self):
        self.cmd += [i for i in self.opts.osubtitle if i not in self.cmd]

    def _add_copy_audio_to_cmd(self):
        self.cmd += ["-acodec", "copy"] if "audio" in self.opts.copy else []

    def _add_copy_video_to_cmd(self):
        self.cmd += ["-vcodec", "copy"] if "video" in self.opts.copy else []

    def _add_copy_subtitle_to_cmd(self):
        self.cmd += ["-scodec", "copy"] if "sub" in self.opts.copy else []

    def _add_copy_all_to_cmd(self):
        self.cmd += ["-codec", "copy"] if "all" in self.opts.copy else []

    def _add_codec_audio_to_cmd(self):
        self.cmd += ["-acodec", self.opts.acodec] if self.opts.acodec else []

    def _add_codec_video_to_cmd(self):
        self.cmd += ["-vcodec", self.opts.vcodec] if self.opts.vcodec else []

    def _add_codec_subtitle_to_cmd(self):
        self.cmd += ["-scodec", self.opts.scodec] if self.opts.scodec else []

    def _add_font_name_to_force_style(self):
        _ = {"FontName": self.opts.FontName}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_font_size_to_force_style(self):
        # Note: abs() is used to prevent "Assertion failed" error from FFmpeg
        _ = {"FontSize": abs(self.opts.FontSize)}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_alignment_to_force_style(self):
        _ = {"Alignment": core.alignments[self.opts.Alignment]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_border_style_to_force_style(self):
        _ = {"BorderStyle": self.opts.BorderStyle}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_primary_colour_to_force_style(self):
        _ = {"PrimaryColour": core.colors[self.opts.PrimaryColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_outline_colour_to_force_style(self):
        _ = {"OutlineColour": core.colors[self.opts.OutlineColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def build(self):
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0] not in ["__init__", "build", "build_force_style"]:
                member[-1]()  # Call all methods of the FFmpeg class

    def build_force_style(self, filename):
        _ = "subtitles=%s:force_style='%s'" % (filename,
                                               self.force_style.template)
        self.cmd += ["-vf", _]


def execute(cmd, top, files):
    for i, file in enumerate(files):
        # Note: Output name is the same as input name
        output = core.create_output(top, file=file)

        # If the output is already in the destination folder...
        if core.path_exists(output):
            # Note: Also for inputs with the same name/different extensions
            # Store as {input : output} to delete the output on exit
            core.not_processed.update({file: output})
        else:
            core.del_on_exit.update({file: output})

        # Note: Copy the original command at every step
        # Finish creating the ultimate FFmpeg command
        new_cmd = cmd.copy() + [output, "-i", file]

        # Note: Convert "int" to "str" to find the length of the precision
        print("[%0*d/%d] Running : '%s'" % (len(str(len(files))), i + 1,
                                            len(files), core.basename(file)))
        try:
            # Note: Disable "Press [q] to stop" feature with DEVNULL
            subprocess.run(new_cmd, check=True, stdin=subprocess.DEVNULL)
            core.del_on_exit.pop(file)  # Pop output to not delete on exit
        except subprocess.CalledProcessError:
            # Note: Output will be deleted on exit
            pass
        except FileNotFoundError:
            print("F : FFmpeg could not be executed")
            return
