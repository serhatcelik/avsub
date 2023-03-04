"""This file contains globals."""

from typing import Dict


class _Globs:
    """Global "control" variables for external modules."""

    _run = True

    _completed: Dict[str, str] = {}

    _corrupted: Dict[str, str] = {}

    _untouched: Dict[str, str] = {}

    @property
    def run(self) -> bool:
        """Controller of the program."""
        return self._run

    @run.setter
    def run(self, run: bool):
        """Setter for the controller."""
        self._run = run

    @property
    def completed(self) -> Dict[str, str]:
        """Completed files."""
        return self._completed

    @property
    def corrupted(self) -> Dict[str, str]:
        """Corrupted files."""
        return self._corrupted

    @property
    def untouched(self) -> Dict[str, str]:
        """Untouched files."""
        return self._untouched


Globs = _Globs()
