"""This file contains globals."""

from dataclasses import dataclass


@dataclass
class Control:
    """Control variables."""

    completed: dict[str, str]
    corrupted: dict[str, str]
    untouched: dict[str, str]

    run: bool = True


Control.completed = {}
Control.corrupted = {}
Control.untouched = {}
