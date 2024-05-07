"""This file contains globals."""

import threading

controller = threading.Event()

completed = {}  # type: dict[str, str]
corrupted = {}  # type: dict[str, str]
untouched = {}  # type: dict[str, str]
