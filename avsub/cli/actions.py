"""Custom actions."""

import argparse
from urllib.error import URLError
from urllib.request import urlopen


class CheckForUpdates(argparse.Action):

    def __init__(self, current: str, url: str, **kwargs):
        super().__init__(nargs=0, **kwargs)

        self.current = current
        self.url = url

    def __call__(self, parser, *args):
        try:
            with urlopen(self.url, timeout=9) as answer:
                latest = answer.readline().rstrip().decode()
        except URLError as err:
            print('[!]', err)
        else:
            if self.current == latest:
                print('[*]', 'Up to date!')
            else:
                print('[*]', f'Update available: {self.current} -> {latest}')
        finally:
            parser.exit()
