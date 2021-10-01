# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This module is used to check for updates."""

from __future__ import absolute_import

from urllib import request

from avsub.core import notice
from avsub.core.tools import repeater


@repeater(retry=3, countdown=5)
def check_for_updates() -> bool:
    """Check if there is a new version for AVsub."""
    with request.urlopen(notice.URL + "/releases/latest/", timeout=10) as rep:  # nosec
        if rep.url != notice.URL + "/releases/tag/" + notice.VERSION:
            latest: str = rep.url.strip(notice.URL + "/releases/tag/")
            print(f"[+] New AVsub version is available ({latest})")
            return True
        print("[*] You have the latest version of AVsub")
        return True
