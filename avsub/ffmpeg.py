"""FFmpeg module."""

from __future__ import annotations

import math
import os
import subprocess as sp  # nosec
from fractions import Fraction
from itertools import chain, count
from typing import TYPE_CHECKING

from avsub.consts import (
    CHOICES_CHANNEL,
    CHOICES_SPEED,
    CHOICES_SUB_ALIGNMENT,
    CHOICES_SUB_BGR_CHART,
    LOGLEVEL,
    X,
)
from avsub.globs import completed, controller, corrupted, untouched

if TYPE_CHECKING:
    from argparse import Namespace


class FFmpeg:
    """FFmpeg handler."""

    cmd = ['ffmpeg', '-n', '-stats']
    style: str

    def build(self, opts: Namespace) -> None:
        """Update the FFmpeg command."""
        cmd = []

        if opts.channel:
            cmd += ['-ac', CHOICES_CHANNEL[opts.channel]]

        if opts.codecA:
            cmd += ['-codec:a', opts.codecA]
        if opts.codecS:
            cmd += ['-codec:s', opts.codecS]
        if opts.codecV:
            cmd += ['-codec:v', opts.codecV]

        cmd += ['-crf', str(opts.compress)]

        cmd += chain(*(['-codec:' + s[0].strip(X), 'copy'] for s in opts.copy))

        if not opts.disable:
            cmd += ['-map', '0']

        if opts.frame is not None:
            cmd += ['-r', str(opts.frame)]

        cmd += opts.onlyA + opts.onlyS + opts.onlyV

        cmd += [f'-{s[0]}n' for s in opts.remove]

        cmd += ['-map_chapters', str(-int(opts.chapters))]
        cmd += ['-map_metadata', str(-int(opts.metadata))]

        if opts.speed is not None:
            speed_a, speed_v = opts.speed
            by_a, by_v = float(Fraction(speed_a)), float(Fraction(speed_v))
            k = CHOICES_SPEED[speed_a]
            n = int(math.log(by_a, k))
            extra = by_a / (k ** n)
            cmd += ['-af', ','.join([f'atempo={k}'] * n + [f'atempo={extra}'])]
            cmd += ['-vf', f'setpts=PTS/{by_v}']

        if opts.trim is not None:
            seek = (opts.trim[0] * 3600) + (opts.trim[1] * 60) + opts.trim[2]
            stop = (opts.trim[3] * 3600) + (opts.trim[4] * 60) + opts.trim[5]
            cmd += ['-ss', str(seek), '-to', str(stop)]

        cmd += ['-loglevel', LOGLEVEL[opts.loglevel]]

        if opts.ffmpeg:
            cmd += opts.ffmpeg.strip().split()

        self.cmd += cmd

        style = []

        style += [f'Fontname={opts.fontname}']
        style += [f'Fontsize={abs(opts.fontsize)}']

        style += [f'PrimaryColour={CHOICES_SUB_BGR_CHART[opts.colorprimary]}']
        style += [f'OutlineColour={CHOICES_SUB_BGR_CHART[opts.coloroutline]}']

        style += [f'Alignment={CHOICES_SUB_ALIGNMENT[opts.alignment]}']

        self.style = ','.join(style)

    def buildsubtitle(self, file: str) -> None:
        """Update the FFmpeg command with the given subtitle file."""
        self.cmd += ['-vf', f"subtitles={file}:force_style='{self.style}'"]

    def execute(self, files: list[str]) -> None:
        """Execute the FFmpeg command."""
        total = len(files)
        align = len(str(total))

        i = count(1)

        while not controller.is_set() and files:
            file = files.pop(0)

            print('[*]', f"Running [{next(i):>{align}}/{total}] -> '{file}'")

            output = untouched[file]

            # Also for files with the same name but different extensions
            if os.path.exists(output):
                print('[ ]', f"File '{output}' already exists. Passing.")
                continue

            cmd = self.cmd + [output, '-i', file]

            try:
                sp.run(cmd, stdin=sp.DEVNULL, check=True)  # nosec
            except FileNotFoundError:
                print('[!]', 'FFmpeg could not be executed. Exiting.')
                return
            except sp.CalledProcessError:
                # Output will be deleted on exit
                corrupted.update({file: untouched.pop(file)})
            else:
                # Output will not be deleted on exit
                completed.update({file: untouched.pop(file)})
