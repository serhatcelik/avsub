"""AVsub — A simplified command-line interface for FFmpeg."""

from __future__ import annotations

import contextlib
import os
import shutil
import signal
import sys
import tempfile
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from typing import TYPE_CHECKING

from avsub.cli import parser
from avsub.consts import X
from avsub.ffmpeg import FFmpeg
from avsub.globs import Control
from avsub.utils import check_for_updates, exit_if_not, line, shut, splitext
from avsub.version import __version__

if TYPE_CHECKING:
    from argparse import Namespace


def start() -> Namespace:
    """Start the program."""
    signal.signal(signal.SIGINT, stop)

    if len(sys.argv) == 1:
        exit_if_not(check_for_updates(__version__))

    opts = parser.parse_args()

    fff = FFmpeg()

    fff.build(opts)  # Start creating the FFmpeg command

    files = exit_if_not(tuple(askopenfilenames(title='Open')))

    # Manual hardsub operation?
    if len(files) == 1 and opts.burn:
        subtitle = exit_if_not(askopenfilename(title='Open subtitle'))

        # For "escaping" nonsense :/
        temp = os.path.join(tempfile.gettempdir(), 'avsub.tmp')

        shutil.copyfile(subtitle, temp)

        fff.build_subtitle(temp.replace('\\', '/').replace(':', '\\\\:'))

    folder = exit_if_not(askdirectory(title='Select a folder', mustexist=True))

    for file in files:
        filename, extension = splitext(os.path.basename(file))

        if opts.extension != X:
            extension = '.' + opts.extension.lstrip('.')

        output = os.path.join(folder, filename + extension)

        Control.corrupted.update({file: output})  # Mark file as "corrupted"

    fff.execute(files)

    return opts


def stop(*args):
    """Stop the program."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    Control.run = False


@line
def log():
    """Print the results."""
    for file in Control.corrupted:
        print('[-]', f"Not completed: '{file}'")
    for file in Control.completed:
        print('[+]', f"Job completed: '{file}'")


def clear(*files: str):
    """Do the cleaning."""
    for file in files:
        with contextlib.suppress(FileNotFoundError, PermissionError):
            os.remove(file)


@line
def brief():
    """Print the summary."""
    success = len(Control.completed)
    failure = len(Control.corrupted)

    print('[*]', f'{success} out of {success + failure} jobs completed.\a')


def main():
    """Entry point."""
    opts = start()

    if Control.run:
        stop()

    log()

    clear(*Control.corrupted.values())

    brief()

    shut(opts.shutdown)


if __name__ == '__main__':
    main()
