"""The dump: the icon and sidebar icon of every device type, laid out for picking in Finder."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from device_icons import coretypes, finder, icns, launchservices
from device_icons.coretypes import TypeDeclaration

DROPPED = ("no type", "no icon", "no sidebar icon")
OURS = ("index.json", "icons", "sidebar", "by-sidebar")


@dataclass(frozen=True)
class Placement:
    """A type's images as found in the iconsets; None where the type has no icon or no sidebar icon."""

    type_identifier: str
    icon: Path | None
    sidebar_icon: Path | None


@dataclass
class Layout:
    """What a dump writes; every path but the sources in files is relative to the output directory."""

    sidebars: dict[str, dict] = field(default_factory=dict)
    dropped: dict[str, list[str]] = field(default_factory=lambda: {reason: [] for reason in DROPPED})
    files: dict[Path, Path] = field(default_factory=dict)
    links: dict[Path, Path] = field(default_factory=dict)
    folders: dict[Path, Path] = field(default_factory=dict)


def layout(placements: dict[str, Placement], resolved: dict[str, str | None]) -> Layout:
    """Return the layout of the placements, grouped by sidebar icon, then icon.

    resolved maps each model identifier to its preferred type identifier, or None for one no type declares.
    A model identifier whose type is missing, or has no icon, or has no sidebar icon, is dropped under that reason.
    A type is placed even if no model identifier resolves to it.
    """
    laid = Layout()
    for placement in sorted(placements.values(), key=lambda placement: placement.type_identifier):
        if placement.icon is None or placement.sidebar_icon is None:
            continue
        icon, sidebar = placement.icon.parent.stem, placement.sidebar_icon.parent.stem
        icon_file, sidebar_file = Path("icons") / f"{icon}.png", Path("sidebar") / f"{sidebar}.png"
        folder = Path("by-sidebar") / sidebar
        laid.files.setdefault(icon_file, placement.icon)
        laid.files.setdefault(sidebar_file, placement.sidebar_icon)
        laid.links.setdefault(folder / f"{icon}.png", icon_file)
        laid.folders.setdefault(folder, sidebar_file)
        group = laid.sidebars.setdefault(sidebar, {"sidebar_icon": sidebar_file.as_posix(), "icons": {}})
        entry = group["icons"].setdefault(icon, {"icon": icon_file.as_posix(), "type_identifiers": [], "model_identifiers": []})
        entry["type_identifiers"].append(placement.type_identifier)
    entries = {
        type_identifier: entry
        for group in laid.sidebars.values()
        for entry in group["icons"].values()
        for type_identifier in entry["type_identifiers"]
    }
    for model_identifier, type_identifier in sorted(resolved.items()):
        placement = placements.get(type_identifier) if type_identifier is not None else None
        if placement is None:
            laid.dropped["no type"].append(model_identifier)
        elif placement.icon is None:
            laid.dropped["no icon"].append(model_identifier)
        elif placement.sidebar_icon is None:
            laid.dropped["no sidebar icon"].append(model_identifier)
        else:
            entries[type_identifier]["model_identifiers"].append(model_identifier)
    for group in laid.sidebars.values():
        group["icons"] = dict(sorted(group["icons"].items()))
    laid.sidebars = dict(sorted(laid.sidebars.items()))
    return laid


def clear(out: Path) -> None:
    """Empty the output directory, creating it if missing.

    Exits if it is not a directory, or holds anything but an earlier dump and .DS_Store.
    """
    if not out.exists():
        out.mkdir(parents=True)
        return
    if not out.is_dir():
        sys.exit(f"{out} is not a directory")
    contents = [path for path in out.iterdir() if path.name != ".DS_Store"]
    if not all(path.name in OURS for path in contents):
        sys.exit(f"{out} is not empty and not an earlier dump; refusing to clear it")
    for path in contents:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


def write(out: Path, laid: Layout) -> None:
    """Clear the output directory, then write the layout's files, relative links, and index.json."""
    clear(out)
    for target, source in laid.files.items():
        (out / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out / target)
    for link, target in laid.links.items():
        (out / link).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(out / target, (out / link).parent), out / link)
    index = {"sidebars": laid.sidebars, "dropped": laid.dropped}
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n")


def dump(out: Path, type_identifiers: list[str] | None = None) -> str:
    """Dump the icons of every device type, or of the given type identifiers, into out; return a summary line.

    Exits if a given type identifier is not declared, or has no icon or no sidebar icon.
    """
    declarations = coretypes.read(coretypes.BUNDLE)
    search = coretypes.bundles(coretypes.BUNDLE)
    if type_identifiers and (unknown := [name for name in type_identifiers if name not in declarations]):
        sys.exit(f"not declared in {coretypes.BUNDLE}: {', '.join(unknown)}")
    model_identifiers = sorted({name for declaration in declarations.values() for name in declaration.model_identifiers})
    preferred = launchservices.preferred_type_identifiers(model_identifiers)
    if type_identifiers:
        chosen = set(type_identifiers)
        resolved: dict[str, str | None] = {name: winner for name, winner in preferred.items() if winner in chosen}
    else:
        chosen = {winner for winner in preferred.values() if winner in declarations}
        resolved = {name: (winner if winner in declarations else None) for name, winner in preferred.items()}
    with tempfile.TemporaryDirectory() as tmp:
        placements = _placements({name: coretypes.inherit(declarations[name], declarations) for name in chosen}, search, Path(tmp))
        if type_identifiers and (lacking := [name for name in type_identifiers if None in (placements[name].icon, placements[name].sidebar_icon)]):
            sys.exit(f"no icon or no sidebar icon in {coretypes.BUNDLE}: {', '.join(lacking)}")
        laid = layout(placements, resolved)
        write(out, laid)
    failed = finder.set_folder_icons({out / folder: out / sidebar for folder, sidebar in laid.folders.items()})
    if failed:
        print(f"no folder icon for {', '.join(str(folder) for folder in failed)}", file=sys.stderr)
    placed = sum(len(entry["model_identifiers"]) for group in laid.sidebars.values() for entry in group["icons"].values())
    icons = sum(len(group["icons"]) for group in laid.sidebars.values())
    dropped = ", ".join(f"{len(names)} {reason}" for reason, names in laid.dropped.items())
    return f"{len(resolved)} model identifiers: {placed} placed under {len(laid.sidebars)} sidebar icons and {icons} icons in {out}; {dropped}"


def _placements(declarations: dict[str, TypeDeclaration], search: list[Path], work: Path) -> dict[str, Placement]:
    needed = {name for declaration in declarations.values() for name in (declaration.icon_file, declaration.sidebar_icon_file) if name}
    found = {name: path for name in needed if (path := coretypes.resource(search, name))}
    with ThreadPoolExecutor() as pool:
        iconsets = dict(zip(found, pool.map(lambda icon_file: icns.iconset(icon_file, work), found.values())))
    placements = {}
    for type_identifier, declaration in declarations.items():
        own = iconsets.get(declaration.icon_file)
        icon = icns.largest(own) if own else None
        sidebar_icon = icns.sidebar_icon(own, iconsets.get(declaration.sidebar_icon_file))
        placements[type_identifier] = Placement(type_identifier, icon, sidebar_icon)
    return placements
