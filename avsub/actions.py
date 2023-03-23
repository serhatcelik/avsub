"""Custom actions."""

import argparse
from typing import Any, Callable


class DoAndExitAction(argparse.Action):

    def __init__(self, func: Callable, fargs: tuple[Any, ...] = (), **kwargs):
        super().__init__(**kwargs)

        self.func = func
        self.fargs = fargs

    def __call__(self, parser, *args):
        parser.exit(self.func(*self.fargs))
