"""General utilities."""

import os
import sys
import webbrowser
from tkinter.messagebox import askokcancel
from typing import Any, NoReturn
from urllib.error import URLError
from urllib.request import urlopen


def check_for_updates(current: str):
    """Check for program updates."""
    file = 'https://raw.githubusercontent.com/serhatcelik/avsub/main/VERSION'

    try:
        with urlopen(file, timeout=9) as answer:  # nosec
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

    zip_ = 'https://github.com/serhatcelik/avsub/archive/refs/heads/main.zip'

    webbrowser.open_new_tab(zip_)


def exit_if_not(thing: Any, /, status: int | str = 0) -> Any | NoReturn:
    """Conditional exit: if not."""
    if not thing:
        sys.exit(status)
    return thing


def separate(func):
    """Draw a horizontal line before and after the given function."""

    def wrapper(*args, **kwargs):
        print('-' * os.get_terminal_size().columns)
        func(*args, **kwargs)
        print('-' * os.get_terminal_size().columns)

    return wrapper


def splitext(path: str) -> tuple[str, str]:
    """Split the pathname `path` into a pair."""
    tail = os.path.split(path)[1]

    extension = ''.join(_[1:]) if (_ := tail.rpartition('.'))[1] else _[1]

    filename = path.removesuffix(extension)

    return filename, extension
