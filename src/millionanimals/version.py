# Adapted from https://github.com/snap-stanford/ogb/blob/master/ogb/version.py

import os
import logging
from threading import Thread

__version__ = "0.1.2"

try:
    os.environ['OUTDATED_IGNORE'] = '1'
    from outdated import check_outdated  # noqa
except ImportError:
    check_outdated = None


def check():
    try:
        is_outdated, latest = check_outdated('millionanimals', __version__)
        if is_outdated:
            logging.warning(
                f'The millionanimals package is out of date. Your version is '
                f'{__version__}, while the latest version is {latest}.')
    except Exception:
        pass


if check_outdated is not None:
    thread = Thread(target=check)
    thread.start()
