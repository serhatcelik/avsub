# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

"""
This module is used to check for updates.
"""

import time
import urllib.error
import urllib.request

from avsub import __license__


def check_for_updates(retry=3, timeout=5):
    url_avsub_tag = "https://github.com/serhatcelik/avsub/releases/tag/"
    url_avsub_latest = "https://github.com/serhatcelik/avsub/releases/latest"

    try:
        with urllib.request.urlopen(url_avsub_latest, timeout=10) as response:
            if response.url != url_avsub_tag + __license__.VERSION:
                version_new = response.url.strip(url_avsub_tag)
                print(f"[+] New AVsub version is available ({version_new})")
                return 0
            print("[*] You have the latest version of AVsub")
            return 0
    except (ValueError, urllib.error.URLError) as err:
        if retry == 0:
            print("[!] Could not check for updates, try again later")
            return 2

        print("[!]", err)
        print("[*] Retrying in %d seconds..." % timeout)

        start = time.monotonic()
        while time.monotonic() - start < timeout:
            continue

        return check_for_updates(retry=retry - 1)
