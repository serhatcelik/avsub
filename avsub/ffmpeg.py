"""FFmpeg module."""

from __future__ import annotations

import os
from itertools import chain
from subprocess import CalledProcessError, DEVNULL as NULL, run
from typing import TYPE_CHECKING

from avsub.consts import CHANNEL, LOGLEVEL, SUB_ALIGNMENT, SUB_BGR_CHART, X
from avsub.globs import Run, completed, corrupted, untouched

if TYPE_CHECKING:
    from argparse import Namespace


class FFmpeg:
    """FFmpeg handler."""

    _cmd = ['ffmpeg', '-n', '-stats']

    _style: str

    def build(self, opts: Namespace):
        """Update the FFmpeg command."""
        cmd = []

        if opts.channel:
            cmd += ['-ac', CHANNEL[opts.channel]]

        if opts.codec_a:
            cmd += ['-codec:a', opts.codec_a]
        if opts.codec_s:
            cmd += ['-codec:s', opts.codec_s]
        if opts.codec_v:
            cmd += ['-codec:v', opts.codec_v]

        cmd += ['-crf', str(opts.compress)]

        cmd += chain(*[['-codec:' + _[0].strip(X), 'copy'] for _ in opts.copy])

        if not opts.disable:
            cmd += ['-map', '0']

        cmd += opts.only_a + opts.only_s + opts.only_v

        cmd += [f'-{_[0]}n' for _ in opts.remove]

        cmd += ['-map_chapters', str(-int(opts.chapters))]
        cmd += ['-map_metadata', str(-int(opts.metadata))]

        if opts.trim is not None:
            seek = (opts.trim[0] * 3600) + (opts.trim[1] * 60) + opts.trim[2]
            stop = (opts.trim[3] * 3600) + (opts.trim[4] * 60) + opts.trim[5]
            cmd += ['-ss', str(seek), '-to', str(stop)]

        cmd += ['-loglevel', LOGLEVEL[opts.loglevel]]

        if opts.ffmpeg_list:
            cmd += opts.ffmpeg_list.strip().split()

        self._cmd += cmd

        style = []

        style += [f'Fontname={opts.font_name}']
        style += [f'Fontsize={abs(opts.font_size)}']

        style += [f'PrimaryColour={SUB_BGR_CHART[opts.color_primary]}']
        style += [f'OutlineColour={SUB_BGR_CHART[opts.color_outline]}']

        style += [f'Alignment={SUB_ALIGNMENT[opts.alignment]}']

        self._style = ','.join(style)

    def build_subtitle(self, file: str):
        """Update the FFmpeg command with the given subtitle."""
        self._cmd += ['-vf', f"subtitles={file}:force_style='{self._style}'"]

    def execute(self, files: tuple[str, ...]):
        """Execute the FFmpeg command."""
        total = len(files)
        align = len(str(total))

        for i, file in enumerate(files):
            if Run.is_set():
                return

            print('[*]', f"Running [{(i + 1):>{align}}/{total}] -> '{file}'")

            output = untouched[file]

            # Also for files with the same name but different extensions
            if os.path.exists(output):
                print(f"File '{output}' already exists. Passing.")
                continue

            try:
                run(self._cmd + [output, '-i', file], stdin=NULL, check=True)
            except FileNotFoundError:
                print('[!]', 'FFmpeg could not be executed. Exiting.')
                return
            except CalledProcessError:
                # Output will be deleted on exit
                corrupted.update({file: untouched.pop(file)})
            else:
                # Output will not be deleted on exit
                completed.update({file: untouched.pop(file)})
