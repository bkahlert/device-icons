"""The icons: the icon and sidebar icon of every device type, laid out for picking in Finder."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from device_icons import coretypes, finder, icns, launchservices, output
from device_icons.coretypes import TypeDeclaration

DROPPED = ("no type", "no icon", "no sidebar icon")
OURS = ("index.json", "README.md", "icons", "sidebar", "by-sidebar")
# The first line of a run's README.md; a README.md without it belongs to someone else and stays.
LEAD = "The icon Finder draws for each model identifier, dumped from `CoreTypes.bundle` by [device-icons](https://github.com/bkahlert/device-icons)."
# Rendered widths in README.md: the icon is 1024 px, the sidebar icon 64 px for a 32 pt slot.
ICON_WIDTH = 128
SIDEBAR_ICON_WIDTH = 32
HEADERS = ("Model identifier", "Type identifier", "Kind", "Icon", "Sidebar icon")
RULE = ("---", "---", "---", ":-:", ":-:")


@dataclass(frozen=True)
class Placement:
    """A type's images as found in the iconsets, None where the type has no icon or no sidebar icon, and its Kind in Finder."""

    type_identifier: str
    icon: Path | None
    sidebar_icon: Path | None
    kind: str = "Mac"


@dataclass(frozen=True)
class Row:
    """One model identifier's row of README.md; the paths are relative to the output directory."""

    model_identifier: str
    type_identifier: str
    kind: str
    icon: Path
    sidebar_icon: Path


@dataclass
class Layout:
    """What a run writes; every path but the sources in files is relative to the output directory."""

    sidebars: dict[str, dict] = field(default_factory=dict)
    dropped: dict[str, list[str]] = field(default_factory=lambda: {reason: [] for reason in DROPPED})
    files: dict[Path, Path] = field(default_factory=dict)
    links: dict[Path, Path] = field(default_factory=dict)
    folders: dict[Path, Path] = field(default_factory=dict)
    rows: list[Row] = field(default_factory=list)


def layout(placements: dict[str, Placement], resolved: dict[str, str | None]) -> Layout:
    """Return the layout of the placements, grouped by sidebar icon, then icon.

    resolved maps each model identifier to its preferred type identifier, or None for one no type declares.
    A model identifier whose type is missing, or has no icon, or has no sidebar icon, is dropped under that reason.
    A type is placed even if no model identifier resolves to it. rows has only the placed model identifiers, grouped by
    sidebar icon and sorted by model identifier within.
    """
    laid = Layout()
    targets: dict[str, tuple[Path, Path]] = {}
    for placement in sorted(placements.values(), key=lambda placement: placement.type_identifier):
        if placement.icon is None or placement.sidebar_icon is None:
            continue
        icon, sidebar = placement.icon.parent.stem, placement.sidebar_icon.parent.stem
        icon_target, sidebar_target = Path("icons") / f"{icon}.png", Path("sidebar") / f"{sidebar}.png"
        folder = Path("by-sidebar") / sidebar
        laid.files.setdefault(icon_target, placement.icon)
        laid.files.setdefault(sidebar_target, placement.sidebar_icon)
        laid.links.setdefault(folder / f"{icon}.png", icon_target)
        laid.folders.setdefault(folder, sidebar_target)
        targets[placement.type_identifier] = (icon_target, sidebar_target)
        group = laid.sidebars.setdefault(sidebar, {"sidebar_icon": sidebar_target.as_posix(), "icons": {}})
        entry = group["icons"].setdefault(icon, {"icon": icon_target.as_posix(), "type_identifiers": [], "model_identifiers": []})
        entry["type_identifiers"].append(placement.type_identifier)
    entries = {type_identifier: entry for group in laid.sidebars.values() for entry in group["icons"].values() for type_identifier in entry["type_identifiers"]}
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
            laid.rows.append(Row(model_identifier, type_identifier, placement.kind, *targets[type_identifier]))
    for group in laid.sidebars.values():
        group["icons"] = dict(sorted(group["icons"].items()))
    laid.sidebars = dict(sorted(laid.sidebars.items()))
    laid.rows.sort(key=lambda row: (row.sidebar_icon.stem, row.model_identifier))
    return laid


def declared(preferred: dict[str, str], declarations: Iterable[str]) -> dict[str, str | None]:
    """Return each model identifier's preferred type identifier as declared, or None where no declaration matches.

    Type identifiers are case-insensitive: LaunchServices returns them lowercased, the bundle declares some with capitals.
    """
    by_lower = {name.lower(): name for name in declarations}
    return {model_identifier: by_lower.get(winner.lower()) for model_identifier, winner in preferred.items()}


def markdown(rows: list[Row], horizontal: bool = False) -> str:
    """Return README.md: LEAD and a table with a row per model identifier, or a column per one if horizontal."""
    cells = [
        (
            row.model_identifier,
            output.code(row.type_identifier),
            row.kind,
            f'<img src="{row.icon.as_posix()}" alt="{row.icon.stem}" width="{ICON_WIDTH}">',
            f'<img src="{row.sidebar_icon.as_posix()}" alt="{row.sidebar_icon.stem}" width="{SIDEBAR_ICON_WIDTH}">',
        )
        for row in rows
    ]
    return "\n".join([LEAD, "", *output.table(HEADERS, RULE, cells, horizontal)]) + "\n"


def write(out: Path, laid: Layout, horizontal: bool = False) -> None:
    """Clear the output directory, then write the layout's files, relative links, index.json, and README.md."""
    output.clear(out, OURS, LEAD)
    for target, source in laid.files.items():
        (out / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out / target)
    for link, target in laid.links.items():
        (out / link).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(out / target, (out / link).parent), out / link)
    index = {"sidebars": laid.sidebars, "dropped": laid.dropped}
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    (out / "README.md").write_text(markdown(laid.rows, horizontal))


def icons(out: Path, type_identifiers: list[str] | None = None, model_identifiers: list[str] | None = None, horizontal: bool = False) -> str:
    """Write the icon and sidebar icon of every device type, or of the given type or model identifiers, into out; return a summary line.

    horizontal lays README.md's table out with a column per model identifier.

    Exits if a given type or model identifier is not declared, a given model identifier resolves to no type, or the
    type has no icon or no sidebar icon, naming the given identifier under the reason.
    """
    declarations = coretypes.read(coretypes.BUNDLE)
    search = coretypes.bundles(coretypes.BUNDLE)
    known = sorted({name for declaration in declarations.values() for name in declaration.model_identifiers})
    unknown = [name for name in type_identifiers or [] if name not in declarations] + [name for name in model_identifiers or [] if name not in known]
    if unknown:
        sys.exit(f"not declared in {coretypes.BUNDLE}: {', '.join(unknown)}")
    resolved = declared(launchservices.preferred_type_identifiers(model_identifiers or known), declarations)
    if model_identifiers and (untyped := [name for name, winner in resolved.items() if winner is None]):
        sys.exit(f"no type in {coretypes.BUNDLE}: {', '.join(untyped)}")
    if type_identifiers:
        chosen = set(type_identifiers)
        resolved = {name: winner for name, winner in resolved.items() if winner in chosen}
    else:
        chosen = {winner for winner in resolved.values() if winner is not None}
    given = [(name, name) for name in type_identifiers or []] + [(name, resolved[name]) for name in model_identifiers or []]
    kinds = {name: finder.kind({name, *coretypes.ancestors(declarations[name], declarations)}) for name in chosen}
    with tempfile.TemporaryDirectory() as tmp:
        placements = _placements({name: coretypes.inherit(declarations[name], declarations) for name in chosen}, kinds, search, Path(tmp))
        lacking = {"no icon": [], "no sidebar icon": []}
        for name, type_identifier in given:
            if placements[type_identifier].icon is None:
                lacking["no icon"].append(name)
            elif placements[type_identifier].sidebar_icon is None:
                lacking["no sidebar icon"].append(name)
        if any(lacking.values()):
            sys.exit("\n".join(f"{reason} in {coretypes.BUNDLE}: {', '.join(names)}" for reason, names in lacking.items() if names))
        laid = layout(placements, resolved)
        write(out, laid, horizontal)
    failed = finder.set_folder_icons({out / folder: out / sidebar for folder, sidebar in laid.folders.items()})
    if failed:
        print(f"no folder icon for {', '.join(str(folder) for folder in failed)}", file=sys.stderr)
    placed = sum(len(entry["model_identifiers"]) for group in laid.sidebars.values() for entry in group["icons"].values())
    icons = sum(len(group["icons"]) for group in laid.sidebars.values())
    dropped = ", ".join(f"{len(names)} {reason}" for reason, names in laid.dropped.items())
    return f"{len(resolved)} model identifiers: {placed} placed under {len(laid.sidebars)} sidebar icons and {icons} icons in {out}; {dropped}"


def _placements(declarations: dict[str, TypeDeclaration], kinds: dict[str, str], search: list[Path], work: Path) -> dict[str, Placement]:
    needed = {name for declaration in declarations.values() for name in (declaration.icon_file, declaration.sidebar_icon_file) if name}
    found = {name: path for name in needed if (path := coretypes.resource(search, name))}
    with ThreadPoolExecutor() as pool:
        iconsets = dict(zip(found, pool.map(lambda icon_file: icns.iconset(icon_file, work), found.values())))
    placements = {}
    for type_identifier, declaration in declarations.items():
        own = iconsets.get(declaration.icon_file)
        icon = icns.largest(own) if own else None
        sidebar_icon = icns.sidebar_icon(own, iconsets.get(declaration.sidebar_icon_file))
        placements[type_identifier] = Placement(type_identifier, icon, sidebar_icon, kinds[type_identifier])
    return placements
