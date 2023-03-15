"""This file contains globals."""


class _Run:
    """Controller class."""

    def __init__(self):
        self._flag = False

    def is_set(self) -> bool:
        """Return true if the internal flag is true."""
        return self._flag

    def set(self):
        """Set the internal flag to true."""
        self._flag = True


Run = _Run()

completed = {}  # type: dict[str, str]
corrupted = {}  # type: dict[str, str]
untouched = {}  # type: dict[str, str]
