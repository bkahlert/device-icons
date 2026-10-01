"""What dump and symbols write alike: the output directory, cleared before a run, and the Markdown table."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def clear(out: Path, ours: tuple[str, ...], lead: str) -> None:
    """Empty the output directory, creating it if missing.

    Exits if it is not a directory, or holds anything but the names in ours and .DS_Store; a README.md among them is
    ours only when it starts with lead.
    """
    if not out.exists():
        out.mkdir(parents=True)
        return
    if not out.is_dir():
        sys.exit(f"{out} is not a directory")
    contents = [path for path in out.iterdir() if path.name != ".DS_Store"]
    if not all(_ours(path, ours, lead) for path in contents):
        sys.exit(f"{out} is not empty and not an earlier run; refusing to clear it")
    for path in contents:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


def _ours(path: Path, ours: tuple[str, ...], lead: str) -> bool:
    if path.name == "README.md":
        return path.is_file() and path.read_text(errors="replace").startswith(lead)
    return path.name in ours


def table(headers: tuple[str, ...], rule: tuple[str, ...], rows: list[tuple[str | None, ...]], horizontal: bool) -> list[str]:
    """Return the lines of a Markdown table with a row per entry of rows, or a column per one if horizontal.

    The first cell of each row is a model identifier, set in code, stacked when horizontal, and empty for None; the
    other cells are written as given. rule is the alignment row under the headers; a horizontal table centres every
    column but the first.
    """
    if horizontal:
        lines = [
            (headers[0], *(stacked(row[0]) for row in rows)),
            ("---", *[":-:"] * len(rows)),
            *((header, *(row[index] for row in rows)) for index, header in enumerate(headers) if index),
        ]
    else:
        lines = [headers, rule, *((code(row[0]), *row[1:]) for row in rows)]
    return [f"| {' | '.join(line)} |" for line in lines]


def code(text: str | None) -> str:
    """Return the text in backticks, or an empty string for None."""
    return f"`{text}`" if text else ""


def stacked(model_identifier: str | None) -> str:
    """Return the model identifier in code, an @KEY=value suffix on two more lines so a column stays narrow; empty for None."""
    if not model_identifier:
        return ""
    head, at, rest = model_identifier.partition("@")
    if not at:
        return f"`{head}`"
    key, equals, value = rest.partition("=")
    return f"`{head}`<br/>`@{key}{equals}`<br/>`{value}`"
