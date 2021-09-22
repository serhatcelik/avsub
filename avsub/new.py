# coding=utf-8
#
# This file is part of AVsub
# See https://github.com/serhatcelik/avsub for more information
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This module is used to check for updates.
"""

from urllib import request

from avsub.core import notice
from avsub.core.tools import repeater


@repeater(retry=3, countdown=5)
def check_for_updates() -> bool:
    with request.urlopen(notice.URL + "/releases/latest/", timeout=10) as rep:
        if rep.url != notice.URL + "/releases/tag/" + notice.VERSION:
            latest: str = rep.url.strip(notice.URL + "/releases/tag/")
            print("[+] New AVsub version is available (%s)" % latest)
            return True
        print("[*] You have the latest version of AVsub")
        return True
