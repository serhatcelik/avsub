"""AVsub — A simplified command-line interface for FFmpeg."""

import os
import shutil
import signal
import subprocess as sp  # nosec
import sys
import tempfile
from contextlib import suppress
from datetime import datetime, timedelta
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from typing import Optional

from avsub.cli import parser
from avsub.consts import (
    X,
)
from avsub.ffmpeg import FFmpeg
from avsub.globs import completed, controller, corrupted, untouched
from avsub.utils import separate, splitext


def start() -> tuple[Optional[int], bool]:
    """Start the program."""
    opts = parser.parse_args()

    signal.signal(signal.SIGINT, stop)

    ff = FFmpeg()

    ff.build(opts)  # Start creating the FFmpeg command

    files = list(askopenfilenames(initialdir='.', title='Open'))

    if not files:
        sys.exit(0)

    # Manual Hardsub Operation?
    if len(files) == 1 and opts.burn:
        subtitle = askopenfilename(title='Open Subtitle')

        if not subtitle:
            sys.exit(0)

        # This is necessary for "escaping" nonsense :/
        tmp = os.path.abspath(os.path.join(tempfile.gettempdir(), 'avsub.tmp'))

        shutil.copyfile(subtitle, tmp)

        tmp = tmp.replace('\\', '/').replace(':', '\\\\:')

        ff.buildsubtitle(tmp)

    folder = askdirectory(initialdir='~', mustexist=True, title='Open Folder')

    if not folder:
        sys.exit(0)

    for file in files:
        filename, extension = splitext(os.path.basename(file))

        if opts.extension != X:
            extension = '.' + opts.extension.lstrip('.')

        output = os.path.abspath(os.path.join(folder, filename + extension))

        untouched.update({file: output})  # Mark file as "untouched"

    ff.execute(files)

    return opts.shutdown, opts.shutdown is not None


def stop(*args) -> None:
    """Stop the program."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    controller.set()


@separate
def log() -> None:
    """Print the results."""
    for file in untouched:
        print('[ ]', f"Not processed: '{file}'")
    for file in corrupted:
        print('[-]', f"Not completed: '{file}'")
    for file in completed:
        print('[+]', f"Job completed: '{file}'")


def clear(*files: str) -> None:
    """Do the cleaning."""
    for file in files:
        with suppress(OSError):
            os.remove(file)


@separate
def brief() -> None:
    """Print the summary."""
    success = len(completed)
    failure = len(corrupted) + len(untouched)

    print('[*]', f'{success} out of {success + failure} jobs completed.\a')


@separate
def shut(timeout: int) -> None:
    """Schedule a shutdown for the machine."""
    sec = abs(timeout)

    try:
        schedule = format(datetime.now() + timedelta(seconds=sec), '%H:%M:%S')
    except OverflowError as err:
        print('[!]', err)
        return

    message = f'AVsub has scheduled a shutdown for {schedule}.'

    shutdown = {
        'linux': (('shutdown', '-P', str(sec), message), '-c'),
        'win32': (('shutdown', '/t', str(sec), '/s', '/c', message), '/a'),
    }

    if sys.platform not in shutdown:
        print('[!]', 'Cannot schedule shutdown on this platform.')
        return

    cmd, cancel = shutdown[sys.platform]

    try:
        sp.check_call(cmd, stdin=sp.DEVNULL, stdout=sp.DEVNULL)  # nosec
    except FileNotFoundError as err:
        print('[!]', err)
    except sp.CalledProcessError:
        pass
    else:
        print('[*]', message, f"Use 'shutdown {cancel}' to cancel.")


def main() -> None:
    """Entry point."""
    timeout, schedule = start()

    log()

    clear(*corrupted.values())

    brief()

    if schedule:
        shut(timeout)


if __name__ == '__main__':
    main()
