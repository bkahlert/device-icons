import sys

import pytest


def pytest_collection_modifyitems(config, items):
    if sys.platform == "darwin":
        return
    skip = pytest.mark.skip(reason="calls iconutil, osascript, or dns-sd")
    for item in items:
        if "macos" in item.keywords:
            item.add_marker(skip)
