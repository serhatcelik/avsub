"""AVsub — A simplified command-line interface for FFmpeg."""

import contextlib
import os
import shutil
import signal
import tempfile
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

from avsub import globs
from avsub.cli import parser
from avsub.consts import X
from avsub.ffmpeg import FFmpeg
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

        globs.untouched.update({file: output})  # Mark file as "untouched"

    fff.execute(files)


def stop(*args):
    """Tell everything to stop themselves."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    globs.run = False


@line
def log():
    """Print the results."""
    for file in globs.untouched:
        print('[ ]', f"Not processed: '{file}'")
    for file in globs.corrupted:
        print('[-]', f"Not completed: '{file}'")
    for file in globs.completed:
        print('[+]', f"Job completed: '{file}'")


def clear(*files: str):
    """Do the cleaning."""
    for file in files:
        with contextlib.suppress(FileNotFoundError, PermissionError):
            os.remove(file)


@line
def brief():
    """Print the summary."""
    success = len(globs.completed)
    failure = len(globs.corrupted) + len(globs.untouched)

    print('[*]', f'{success} out of {success + failure} jobs completed.\a')


def main():
    """Entry point."""
    start()

    if globs.run:
        stop()

    log()

    clear(*globs.corrupted.values())

    brief()


if __name__ == '__main__':
    main()
