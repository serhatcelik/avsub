# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""This module is used to check for updates."""

from __future__ import absolute_import

import urllib.error
from urllib.request import urlopen

from avsub.core import consts
from avsub.core import notice_
from avsub.core.tools import repeater


@repeater(retry=3, countdown=5)
def check_for_updates() -> bool:
    """Check if there is a new version for AVsub."""
    with urlopen(consts.URL_LATEST, timeout=10) as rep:  # nosec
        if rep.url != consts.URL_TAG + notice_.VERSION:
            latest: str = rep.url.strip(consts.URL_TAG)
            print(f"[+] Recommended AVsub version is available ({latest})")
            return True
        print(f"[*] You have the latest version of AVsub ({notice_.VERSION})")
        return True


def check_for_yanked() -> bool:
    """Check if the current version is a yanked version."""
    try:
        with urlopen(consts.URL_YANKED, timeout=10) as versions:  # nosec
            for yanked in versions.read().decode("utf-8").split():
                if notice_.VERSION == yanked:
                    return True
    except urllib.error.URLError:
        pass
    return False
