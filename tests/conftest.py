import os
import stat
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    if sys.platform == "darwin":
        return
    skip = pytest.mark.skip(reason="calls iconutil, osascript, or dns-sd")
    for item in items:
        if "macos" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def fake_command(tmp_path, monkeypatch):
    bin = tmp_path / "bin"
    bin.mkdir()
    monkeypatch.setenv("PATH", f"{bin}{os.pathsep}{os.environ['PATH']}")

    def fake(name: str, then: str = "") -> Fake:
        log = tmp_path / f"{name}.log"
        script = bin / name
        script.write_text(f'#!/bin/sh\nprintf "%s %s\\n" "$$" "$*" >> "{log}"\n{then}\n')
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return Fake(log)

    return fake


@dataclass(frozen=True)
class Fake:
    log: Path

    def calls(self, at_least: int = 1) -> list[tuple[int, str]]:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            lines = self.log.read_text().splitlines() if self.log.exists() else []
            if len(lines) >= at_least:
                return [(int(pid), arguments) for pid, arguments in (line.split(" ", 1) for line in lines)]
            time.sleep(0.01)
        raise TimeoutError(f"{at_least} calls not logged within 5 s")
