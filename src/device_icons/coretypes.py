"""Type declarations of Apple devices, read from CoreTypes.bundle."""

from __future__ import annotations

import plistlib
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path

BUNDLE = Path("/System/Library/CoreServices/CoreTypes.bundle")
MODEL_IDENTIFIER_TAG_CLASS = "com.apple.device-model-code"


@dataclass(frozen=True)
class TypeDeclaration:
    """One entry of UTExportedTypeDeclarations, reduced to what places a device icon."""

    type_identifier: str
    model_identifiers: tuple[str, ...] = ()
    conforms_to: tuple[str, ...] = ()
    icon_file: str | None = None
    sidebar_icon_file: str | None = None
    symbol_name: str | None = None


def bundles(root: Path) -> list[Path]:
    """Return the bundle followed by the bundles nested in its Contents/Library, sorted by name."""
    library = root / "Contents" / "Library"
    nested = sorted(path for path in library.iterdir() if path.suffix == ".bundle") if library.is_dir() else []
    return [root, *nested]


def read(root: Path) -> dict[str, TypeDeclaration]:
    """Return the type declarations of the bundle and its nested bundles by type identifier.

    Of several declarations of one type identifier the first in bundles(root) order wins.
    A bundle without Contents/Info.plist is skipped.
    """
    declarations: dict[str, TypeDeclaration] = {}
    for bundle in bundles(root):
        info = bundle / "Contents" / "Info.plist"
        if not info.is_file():
            continue
        with info.open("rb") as file:
            exported = plistlib.load(file).get("UTExportedTypeDeclarations", [])
        for entry in exported:
            icons = entry.get("UTTypeIcons", {})
            declaration = TypeDeclaration(
                type_identifier=entry["UTTypeIdentifier"],
                model_identifiers=_strings(entry.get("UTTypeTagSpecification", {}).get(MODEL_IDENTIFIER_TAG_CLASS)),
                conforms_to=_strings(entry.get("UTTypeConformsTo")),
                icon_file=icons.get("UTTypeIconFile") or entry.get("UTTypeIconFile"),
                sidebar_icon_file=icons.get("_UTTypeTemplateIconFile"),
                symbol_name=icons.get("UTTypeSymbolName"),
            )
            declarations.setdefault(declaration.type_identifier, declaration)
    return declarations


def inherit(declaration: TypeDeclaration, declarations: dict[str, TypeDeclaration]) -> TypeDeclaration:
    """Return the declaration with a missing icon file or sidebar icon file taken from the nearest type it conforms to.

    Parents are searched breadth first; unknown parents are skipped, and each type is visited once.
    """
    queue, seen = deque(declaration.conforms_to), set()
    while queue and (declaration.icon_file is None or declaration.sidebar_icon_file is None):
        type_identifier = queue.popleft()
        if type_identifier in seen or type_identifier not in declarations:
            continue
        seen.add(type_identifier)
        parent = declarations[type_identifier]
        if declaration.icon_file is None and parent.icon_file is not None:
            declaration = replace(declaration, icon_file=parent.icon_file)
        if declaration.sidebar_icon_file is None and parent.sidebar_icon_file is not None:
            declaration = replace(declaration, sidebar_icon_file=parent.sidebar_icon_file)
        queue.extend(parent.conforms_to)
    return declaration


def ancestors(declaration: TypeDeclaration, declarations: dict[str, TypeDeclaration]) -> set[str]:
    """Return every type identifier the declaration conforms to, directly or through its parents.

    Unknown parents are included by name but not followed; each type is visited once.
    """
    found, queue = set(), deque(declaration.conforms_to)
    while queue:
        type_identifier = queue.popleft()
        if type_identifier in found:
            continue
        found.add(type_identifier)
        if type_identifier in declarations:
            queue.extend(declarations[type_identifier].conforms_to)
    return found


def resource(search: list[Path], name: str) -> Path | None:
    """Return the file of that name in the Contents/Resources of the first bundle that has it, or None."""
    return next((path for bundle in search if (path := bundle / "Contents" / "Resources" / name).is_file()), None)


def _strings(value: str | list[str] | None) -> tuple[str, ...]:
    if value is None:
        return ()
    return (value,) if isinstance(value, str) else tuple(value)
