"""This file contains globals."""


class Control:
    run = True

    completed: dict[str, str] = {}

    corrupted: dict[str, str] = {}

    untouched: dict[str, str] = {}
