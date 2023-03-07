"""This file contains globals."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Control:
    """Control variables."""

    completed: Dict[str, str]
    corrupted: Dict[str, str]
    untouched: Dict[str, str]

    run: bool = True


Control.completed = {}
Control.corrupted = {}
Control.untouched = {}
