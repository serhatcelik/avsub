"""Custom actions."""

import argparse
from typing import Any, Callable, Iterable


class DoAndExitAction(argparse.Action):

    def __init__(self, func: Callable, args: Iterable[Any] = (), **kwargs):
        super().__init__(**kwargs)

        self.func = func
        self.args = args

    def __call__(self, parser, *args):
        parser.exit(self.func(*self.args))
