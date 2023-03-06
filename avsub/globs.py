"""This file contains globals."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Control:
    """Control variables."""

    run: bool

    completed: Dict[str, str]
    corrupted: Dict[str, str]
    untouched: Dict[str, str]


Control.run = True

Control.completed = {}
Control.corrupted = {}
Control.untouched = {}
