"""This file contains globals."""

from threading import Event

Run = Event()

completed = {}  # type: dict[str, str]
corrupted = {}  # type: dict[str, str]
untouched = {}  # type: dict[str, str]
