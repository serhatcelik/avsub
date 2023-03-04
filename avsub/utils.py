"""General utilities."""

import os
import sys
from typing import Any, Callable, Tuple


def exit_if_not(thing: Any, /, status: int = 0) -> Any:
    """Conditional exit: if not."""
    if not thing:
        sys.exit(status)
    return thing


def line(func: Callable[[], Any]) -> Callable[[], None]:
    """Draw a horizontal line before and after the given function."""

    def wrapper():
        """Wrapper function."""
        print('-' * (os.get_terminal_size().columns - 1))
        func()
        print('-' * (os.get_terminal_size().columns - 1))

    return wrapper


def splitext(path: str) -> Tuple[str, str]:
    """Split the pathname `path` into a pair."""
    tail = os.path.split(path)[1]

    extension = ''.join(_[1:]) if (_ := tail.rpartition('.'))[1] else _[1]

    filename = path.removesuffix(extension)

    return filename, extension
