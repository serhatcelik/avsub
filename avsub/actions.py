"""Custom argument actions."""

import argparse
from typing import Any, Callable


class ExitAction(argparse.Action):
    """This expects a "func" keyword, executes the given function and exits."""

    def __init__(self, func: Callable, args: tuple[Any, ...] = (), **kwargs):
        super().__init__(**kwargs)

        self.func = func
        self.args = args

    def __call__(self, parser, *args):
        parser.exit(self.func(*self.args))
