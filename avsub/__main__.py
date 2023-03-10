"""AVsub — A simplified command-line interface for FFmpeg."""

import contextlib
import os
import shutil
import signal
import sys
import tempfile
from datetime import datetime, timedelta
from subprocess import CalledProcessError, DEVNULL as NULL, check_call  # nosec
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

from avsub.cli import parser
from avsub.consts import X
from avsub.ffmpeg import FFmpeg
from avsub.globs import Control
from avsub.utils import check_for_updates, exit_if_not, line, splitext
from avsub.version import __version__


def start() -> tuple[int | None, bool]:
    """Start the program."""
    signal.signal(signal.SIGINT, stop)

    if len(sys.argv) == 1:
        check_for_updates(__version__)
        sys.exit()

    opts = parser.parse_args()

    fff = FFmpeg()

    fff.build(opts)  # Start creating the FFmpeg command

    exit_if_not(files := tuple(askopenfilenames(title='Open')))

    # Manual hardsub operation?
    if len(files) == 1 and opts.burn:
        exit_if_not(subtitle := askopenfilename(title='Open subtitle'))

        # For "escaping" nonsense :/
        tmp = os.path.abspath(os.path.join(tempfile.gettempdir(), 'avsub.tmp'))

        shutil.copyfile(subtitle, tmp)

        fff.build_subtitle(tmp.replace('\\', '/').replace(':', '\\\\:'))

    exit_if_not(folder := askdirectory(title='Select folder', mustexist=True))

    for file in files:
        filename, extension = splitext(os.path.basename(file))

        if opts.extension != X:
            extension = '.' + opts.extension.lstrip('.')

        output = os.path.abspath(os.path.join(folder, filename + extension))

        Control.untouched.update({file: output})  # Mark file as "untouched"

    fff.execute(files)

    return opts.shutdown, opts.shutdown is not None


def stop(*args):
    """Stop the program."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    Control.run = False


@line
def log():
    """Print the results."""
    for file in Control.untouched:
        print('[ ]', f"Not processed: '{file}'")
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
    failure = len(Control.corrupted) + len(Control.untouched)

    print('[*]', f'{success} out of {success + failure} jobs completed.\a')


@line
def shut(timeout: int):
    """Schedule a shutdown for the machine."""
    timeout = abs(timeout)

    schedule = format(datetime.now() + timedelta(seconds=timeout), '%H:%M:%S')

    wall = f'AVsub has scheduled a shutdown for {schedule}.'

    cmd = ['shutdown', '/s', '/t', str(timeout), '/c', wall, '/d', 'p:0:0']

    try:
        check_call(cmd, stdin=NULL, stdout=NULL, stderr=NULL)
    except (FileNotFoundError, CalledProcessError):
        print('[!]', "Cannot schedule shutdown or there's a pending shutdown.")
    else:
        print('[*]', wall, "Use 'shutdown /a' to cancel.")


def main():
    """Entry point."""
    timeout, schedule = start()

    if Control.run:
        stop()

    log()

    clear(*Control.corrupted.values())

    brief()

    if schedule:
        shut(timeout)


if __name__ == '__main__':
    main()
