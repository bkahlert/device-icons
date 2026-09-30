"""Iconsets, unpacked from icon files with iconutil."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ICON_IMAGE = re.compile(r"^icon_(?P<side>\d+)x(?P=side)(?:@(?P<scale>\d)x)?\.png$")
SIDEBAR_IMAGE = "32x32@2x.png"


def iconset(icon_file: Path, work: Path) -> Path:
    """Return work/<icon file stem>.iconset, unpacking the icon file into it unless it exists."""
    target = work / f"{icon_file.stem}.iconset"
    if not target.exists():
        subprocess.run(["iconutil", "-c", "iconset", "-o", target, icon_file], check=True, stdout=subprocess.DEVNULL)
    return target


def pixels(name: str) -> int:
    """Return the pixel width of an icon_<side>x<side>[@<scale>x].png image name, 0 for any other name."""
    match = ICON_IMAGE.match(name)
    return int(match["side"]) * int(match["scale"] or 1) if match else 0


def largest(iconset: Path) -> Path | None:
    """Return the icon image with the most pixels in the iconset, or None if it has none."""
    images = [path for path in iconset.iterdir() if pixels(path.name)]
    return max(images, key=lambda path: pixels(path.name), default=None)


def sidebar_icon(own: Path | None, sidebar_file: Path | None) -> Path | None:
    """Return the 64 px sidebar image of a type, or None if there is none.

    The template image embedded in the type's own iconset wins over the image of the iconset of its sidebar icon file.
    """
    candidates = [own and own / f"template_{SIDEBAR_IMAGE}", sidebar_file and sidebar_file / f"icon_{SIDEBAR_IMAGE}"]
    return next((path for path in candidates if path and path.is_file()), None)
