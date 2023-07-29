"""Custom argument actions."""

import argparse
from typing import Any, Callable


class ExitAction(argparse.Action):
    """Execute the function and exit."""

    def __init__(self, f: Callable, args: tuple[Any, ...] = (), **kwargs):
        super().__init__(nargs=0, **kwargs)

        self.f = f
        self.args = args

    def __call__(self, parser, *args):
        parser.exit(self.f(*self.args))
