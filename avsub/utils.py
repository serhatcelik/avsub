"""General utilities."""

import functools
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
            latest = answer.readline().decode().rstrip()
    except URLError as err:
        print('[!]', err)
        return

    if current == latest:
        print('[*]', 'Up to date!')
        return

    print('[*]', message := 'Update available. Download?')

    if not askokcancel(message=message, icon='warning'):
        return

    zipp = 'https://github.com/serhatcelik/avsub/archive/refs/heads/main.zip'

    webbrowser.open_new_tab(zipp)


def exit_if_not(thing: Any, /, status: int | str = 0) -> Any | NoReturn:
    """Conditional exit: if not."""
    if not thing:
        sys.exit(status)
    return thing


def separate(f):
    """Draw a horizontal line before and after the given function."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        print('-' * os.get_terminal_size().columns)
        f(*args, **kwargs)
        print('-' * os.get_terminal_size().columns)

    return wrapper


def splitext(path: str) -> tuple[str, str]:
    """Split the pathname `path` into a pair."""
    tail = os.path.split(path)[1]

    sep, extension = tail.rpartition('.')[1:]

    extension = (sep + extension) if sep else sep

    filename = path.removesuffix(extension)

    return filename, extension
