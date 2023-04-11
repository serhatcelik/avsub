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
from typing import NoReturn

from avsub.cli import parser
from avsub.consts import X
from avsub.ffmpeg import FFmpeg
from avsub.globs import controller, completed, corrupted, untouched
from avsub.utils import exit_if_not, separate, splitext


def start() -> tuple[int | None, bool]:
    """Start the program."""
    sys.excepthook = stop_hard

    signal.signal(signal.SIGINT, stop)

    opts = parser.parse_args()

    ff = FFmpeg()

    ff.build(opts)  # Start creating the FFmpeg command

    exit_if_not(files := list(askopenfilenames(title='Open')))

    # Manual Hardsub Operation?
    if len(files) == 1 and opts.burn:
        exit_if_not(subtitle := askopenfilename(title='Open Subtitle'))

        # This is necessary for "escaping" nonsense :/
        tmp = os.path.abspath(os.path.join(tempfile.gettempdir(), 'avsub.tmp'))

        shutil.copyfile(subtitle, tmp)

        tmp = tmp.replace('\\', '/').replace(':', '\\\\:')

        ff.build_subtitle(tmp)

    exit_if_not(folder := askdirectory(title='Select Folder', mustexist=True))

    for file in files:
        filename, extension = splitext(os.path.basename(file))

        if opts.extension != X:
            extension = '.' + opts.extension.lstrip('.')

        output = os.path.abspath(os.path.join(folder, filename + extension))

        untouched.update({file: output})  # Mark file as "untouched"

    ff.execute(files)

    return opts.shutdown, opts.shutdown is not None


def stop(*args):
    """Stop the program."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    controller.set()


def stop_hard(*args) -> NoReturn:
    """Stop the program the hard way."""
    os._exit(-1)


@separate
def log():
    """Print the results."""
    for file in untouched:
        print('[ ]', f"Not processed: '{file}'")
    for file in corrupted:
        print('[-]', f"Not completed: '{file}'")
    for file in completed:
        print('[+]', f"Job completed: '{file}'")


def clear(*files: str):
    """Do the cleaning."""
    for file in files:
        with suppress(FileNotFoundError, PermissionError):
            os.remove(file)


@separate
def brief():
    """Print the summary."""
    success = len(completed)
    failure = len(corrupted) + len(untouched)

    print('[*]', f'{success} out of {success + failure} jobs completed.\a')


@separate
def shut(timeout: int):
    """Schedule a shutdown for the machine."""
    timeout = abs(timeout)

    schedule = format(datetime.now() + timedelta(seconds=timeout), '%H:%M:%S')

    msg = f'AVsub has scheduled a shutdown for {schedule}.'

    shutdown = {
        'linux': ['shutdown', '-P', str(timeout), msg],
        'win32': ['shutdown', '/t', str(timeout), '/s', '/c', msg],
    }

    if sys.platform not in shutdown:
        print('[!]', 'Cannot schedule shutdown on this platform.')
        return

    cmd = shutdown[sys.platform]

    try:
        sp.check_call(cmd, stdin=sp.DEVNULL, stdout=sp.DEVNULL)  # nosec
    except FileNotFoundError as err:
        print('[!]', err)
    except sp.CalledProcessError:
        pass


def main():
    """Entry point."""
    timeout, schedule = start()

    log()

    clear(*corrupted.values())

    brief()

    if schedule:
        shut(timeout)


if __name__ == '__main__':
    main()
