# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import os
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

    def _add_ac_to_cmd(self):
        self.cmd += ["-ac", core.acs[self.opts.ac]] if self.opts.ac else []

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
        self.cmd += [_ for _ in self.opts.oaudio if _ not in self.cmd]

    def _add_only_video_to_cmd(self):
        self.cmd += [_ for _ in self.opts.ovideo if _ not in self.cmd]

    def _add_only_subtitle_to_cmd(self):
        self.cmd += [_ for _ in self.opts.osubtitle if _ not in self.cmd]

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

    def _add_fontname_to_force_style(self):
        _ = {"FontName": self.opts.FontName}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_fontsize_to_force_style(self):
        # Note: "abs" is used to prevent "Assertion failed" error from FFmpeg
        _ = {"FontSize": abs(self.opts.FontSize)}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_alignment_to_force_style(self):
        _ = {"Alignment": core.alignments[self.opts.Alignment]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_borderstyle_to_force_style(self):
        _ = {"BorderStyle": self.opts.BorderStyle}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_primarycolour_to_force_style(self):
        _ = {"PrimaryColour": core.colors[self.opts.PrimaryColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def _add_outlinecolour_to_force_style(self):
        _ = {"OutlineColour": core.colors[self.opts.OutlineColour]}
        self.force_style = string.Template(self.force_style.safe_substitute(_))

    def build(self):
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0] not in ["__init__", "build", "build_force_style"]:
                member[-1]()  # Call the method of the FFmpeg class

    def build_force_style(self, filename):
        self.cmd += [
            "-filter:v",
            "subtitles=%s:force_style='%s'" % (filename,
                                               self.force_style.template)
        ]


def execute(cmd, files):
    """
    Finish creating the ultimate FFmpeg command and execute it.

    :param cmd: FFmpeg command to finish creating.
    :param files: All files to process.
    """

    top = getattr(core, "a_temp")  # Top folder that will contain all files

    print("Getting ready to start...")
    # Mark all files as "not processed" before start processing
    for file in files:  # avsub: C1020
        core.not_processed.update({file: core.create_output(top, file=file)})

    for i, file in enumerate(files):
        # Note: Output base name is the same as input base name
        output = core.not_processed[file]

        # If the output is already in the destination folder...
        if core.path_exists(output):
            # Note: Also for inputs with the same name but different extensions
            pass
        else:
            # Store as {input: output} to delete the output on exit
            core.del_on_exit.update({file: output})
            if file in core.not_processed:
                # Note: Output is no longer marked as "not processed"
                core.not_processed.pop(file)

        # Note: Convert "int" to "str" to find the length of the precision
        print("Running [%*d/%d]: '%s'" % (len(str(len(files))), i + 1,
                                          len(files), core.basename(file)))
        if getattr(core, "opts").show_ffmpeg:
            # If the operation is not HARDSUB MANUAL...
            if not getattr(core, "opts").embed:  # avsub: C1110
                print("-" * os.get_terminal_size().columns)
                print("%s \"%s\" -i \"%s\"" % (" ".join(cmd), output, file))
                print("-" * os.get_terminal_size().columns)

        # Finish creating the ultimate FFmpeg command
        new_cmd = cmd + [output, "-i", file]
        try:
            # Note: Disable "Press [q] to stop" feature with "DEVNULL"
            subprocess.run(new_cmd, check=True, stdin=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Note: Output will be deleted on exit
            pass
        except FileNotFoundError:
            # Set attribute for "Over Control"
            setattr(core, "fatal_ffmpeg", core.basename(file))
            print("FFmpeg could not be executed (fatal)")
            return
        else:
            if file in core.del_on_exit:
                core.del_on_exit.pop(file)  # Pop output to not delete on exit
