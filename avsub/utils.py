"""General utilities."""

import os
import sys
import webbrowser
from datetime import datetime, timedelta
from subprocess import CalledProcessError, DEVNULL as NULL, check_call  # nosec
from tkinter.messagebox import askokcancel
from typing import Any, Optional
from urllib.error import URLError
from urllib.request import urlopen


def check_for_updates(current: str):
    """Check for the program updates."""
    raw = 'https://raw.githubusercontent.com/serhatcelik/avsub/main/VERSION'

    try:
        with urlopen(raw, timeout=10) as answer:  # nosec
            latest = answer.readline().rstrip().decode()
    except URLError as err:
        print('[!]', err)
        return

    if current == latest:
        print('[*]', 'Up to date!')
        return

    print('[*]', message := 'Update available. Download?')

    if not askokcancel(message=message, icon='warning'):
        return

    ref = 'https://github.com/serhatcelik/avsub/archive/refs/heads/main.zip'

    webbrowser.open_new_tab(ref)


def exit_if_not(thing: Any, /, status: int = 0) -> Any:
    """Conditional exit: if not."""
    if not thing:
        sys.exit(status)
    return thing


def line(func):
    """Draw a horizontal line before and after the given function."""

    def _(*args, **kwargs):
        print('-' * (os.get_terminal_size().columns - 1))
        func(*args, **kwargs)
        print('-' * (os.get_terminal_size().columns - 1))

    return _


def shut(timeout: Optional[int]):
    """Shut down the machine."""
    if timeout is None:
        return

    timeout = abs(timeout)

    schedule = format(datetime.now() + timedelta(seconds=timeout), '%H:%M:%S')

    wall = f'AVsub has scheduled a shutdown for {schedule}.'

    command = ['shutdown', '/s', '/t', str(timeout), '/c', wall, '/d', 'p:0:0']

    try:
        check_call(command, stdin=NULL, stdout=NULL, stderr=NULL)
    except (FileNotFoundError, CalledProcessError) as err:
        print('[!]', err)


def splitext(path: str) -> tuple[str, str]:
    """Split the pathname `path` into a pair."""
    tail = os.path.split(path)[1]

    extension = ''.join(_[1:]) if (_ := tail.rpartition('.'))[1] else _[1]

    filename = path.removesuffix(extension)

    return filename, extension
