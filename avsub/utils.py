"""General utilities."""

import os
import sys
from typing import Any, NoReturn


def exit_if_not(thing: Any, /, status: int | str = 0) -> Any | NoReturn:
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


def splitext(path: str) -> tuple[str, str]:
    """Split the pathname `path` into a pair."""
    tail = os.path.split(path)[1]

    extension = ''.join(_[1:]) if (_ := tail.rpartition('.'))[1] else _[1]

    filename = path.removesuffix(extension)

    return filename, extension
