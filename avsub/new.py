# This file is part of AVsub
# Released under the GNU General Public License v3.0
# Copyright (C) Serhat Çelik

import urllib.error
import urllib.request
from avsub import __license__


def check_for_updates():
    url_avsub_tag = "https://github.com/serhatcelik/avsub/releases/tag/"
    url_avsub_latest = "https://github.com/serhatcelik/avsub/releases/latest"

    try:
        with urllib.request.urlopen(url_avsub_latest, timeout=10) as response:
            if response.url != url_avsub_tag + __license__.VERSION:
                latest_version = response.url.strip(url_avsub_tag)
                return "New AVsub version is available (%s)" % latest_version
            return "You have the latest version of AVsub"
    except (ValueError, urllib.error.URLError):
        return "Could not check for updates"
