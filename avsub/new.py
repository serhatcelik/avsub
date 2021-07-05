# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import time
import urllib.error
import urllib.request

from avsub.__license__ import VERSION


def check_for_updates(retry, timeout):
    """
    Check if there is a new version for AVsub.

    :param retry: Maximum number of retries.
    :param timeout: Timeout to wait before each retry.
    """

    url_avsub_tag = "https://github.com/serhatcelik/avsub/releases/tag/"
    url_avsub_latest = "https://github.com/serhatcelik/avsub/releases/latest"

    try:
        with urllib.request.urlopen(url_avsub_latest, timeout=5) as response:
            if response.url != url_avsub_tag + VERSION:
                version_new = response.url.strip(url_avsub_tag)
                return "[+] New AVsub version is available (%s)" % version_new
            return "[*] You have the latest version of AVsub (%s)" % VERSION
    except (ValueError, urllib.error.URLError) as err:
        if retry == 0:
            return "[!] Could not check for updates, try again later"

        print("[!] %s" % err)
        print("[*] Retrying in %d seconds..." % timeout)  # avsub: C1201

        start = time.monotonic()
        while time.monotonic() - start < timeout:
            pass

        return check_for_updates(retry=retry - 1, timeout=timeout)
