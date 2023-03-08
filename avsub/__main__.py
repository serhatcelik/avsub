"""AVsub — A simplified command-line interface for FFmpeg."""

import contextlib
import os
import shutil
import signal
import tempfile
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

from avsub.cli import parser
from avsub.consts import X
from avsub.ffmpeg import FFmpeg
from avsub.globs import Control
from avsub.utils import exit_if_not, line, splitext


def start():
    """Start the program."""
    signal.signal(signal.SIGINT, stop)

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

        Control.untouched.update({file: output})  # Mark file as "untouched"

    fff.execute(files)


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


def main():
    """Entry point."""
    start()

    if Control.run:
        stop()

    log()

    clear(*Control.corrupted.values())

    brief()


if __name__ == '__main__':
    main()
