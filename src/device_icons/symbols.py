"""The symbols: the SF Symbol of every device type as SVG, with the model identifiers that get it."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from device_icons import coreglyphs, coretypes, launchservices, output
from device_icons.coreglyphs import HIERARCHY, Outline
from device_icons.icons import declared

DROPPED = ("no type", "no symbol name", "no symbol")
OURS = ("index.json", "README.md", "symbols")
# The first line of a run's README.md; a README.md without it belongs to someone else and stays.
LEAD = "The SF Symbol of each model identifier's type, written as SVG from `CoreGlyphs.bundle` by [device-icons](https://github.com/bkahlert/device-icons)."
SYMBOL_WIDTH = 64
HEADERS = ("Model identifier", "Type identifier", "Symbol name", "Symbol")
RULE = ("---", "---", "---", ":-:")


@dataclass(frozen=True)
class Row:
    """One row of README.md: a model identifier and its type, or neither for a given symbol no model identifier gets."""

    model_identifier: str | None
    type_identifier: str | None
    symbol_name: str
    symbol: Path


@dataclass
class Layout:
    """What a run writes; every path is relative to the output directory, and files maps each onto its SVG."""

    symbols: dict[str, dict] = field(default_factory=dict)
    dropped: dict[str, list[str]] = field(default_factory=lambda: {reason: [] for reason in DROPPED})
    files: dict[Path, str] = field(default_factory=dict)
    rows: list[Row] = field(default_factory=list)


def layout(
    names: dict[str, str | None],
    resolved: dict[str, str | None],
    outlines: dict[str, Outline | None],
    given: list[str],
    hierarchy: tuple[float, float, float] = HIERARCHY,
) -> Layout:
    """Return the layout: a symbol per name with the types and model identifiers that get it, and a row per model identifier.

    names maps each type identifier to its current symbol name, None where it and its parents declare none. resolved
    maps each model identifier to its preferred type identifier, None for one no type declares. outlines maps each
    symbol name to its outline, None where CoreGlyphs.bundle has no such symbol. given lists the current symbol names
    asked for, each with an outline; each is placed even if no type has it, and gets a row with empty identifiers if no
    model identifier gets it. hierarchy gives the opacity of a primary, secondary, and tertiary layer in the SVGs.
    A model identifier whose type is missing, or has no symbol name, or whose symbol name has no symbol, is dropped
    under that reason. Symbols, their identifiers, rows, and the dropped are sorted; rows are grouped by symbol name.
    """
    laid = Layout()
    for type_identifier, name in sorted(names.items()):
        if name is not None and outlines.get(name) is not None:
            _place(laid, name, outlines[name], hierarchy)["type_identifiers"].append(type_identifier)
    for name in dict.fromkeys(given):
        _place(laid, name, outlines[name], hierarchy)
    for model_identifier, type_identifier in sorted(resolved.items()):
        name = names.get(type_identifier) if type_identifier is not None else None
        if type_identifier is None or type_identifier not in names:
            laid.dropped["no type"].append(model_identifier)
        elif name is None:
            laid.dropped["no symbol name"].append(model_identifier)
        elif outlines.get(name) is None:
            laid.dropped["no symbol"].append(model_identifier)
        else:
            entry = laid.symbols[name]
            entry["model_identifiers"].append(model_identifier)
            laid.rows.append(Row(model_identifier, type_identifier, name, Path(entry["symbol"])))
    for name in dict.fromkeys(given):
        if not laid.symbols[name]["model_identifiers"]:
            laid.rows.append(Row(None, None, name, Path(laid.symbols[name]["symbol"])))
    laid.symbols = dict(sorted(laid.symbols.items()))
    laid.rows.sort(key=lambda row: (row.symbol_name, row.model_identifier or ""))
    return laid


def _place(laid: Layout, name: str, outline: Outline, hierarchy: tuple[float, float, float]) -> dict:
    target = Path("symbols") / f"{name}.svg"
    laid.files.setdefault(target, coreglyphs.svg(outline, hierarchy))
    return laid.symbols.setdefault(name, {"symbol": target.as_posix(), "type_identifiers": [], "model_identifiers": []})


def markdown(rows: list[Row], horizontal: bool = False) -> str:
    """Return README.md: LEAD and a table with a row per model identifier, or a column per one if horizontal."""
    cells = [
        (
            row.model_identifier,
            output.code(row.type_identifier),
            output.code(row.symbol_name),
            f'<img src="{row.symbol.as_posix()}" alt="{row.symbol_name}" width="{SYMBOL_WIDTH}">',
        )
        for row in rows
    ]
    return "\n".join([LEAD, "", *output.table(HEADERS, RULE, cells, horizontal)]) + "\n"


def write(out: Path, laid: Layout, horizontal: bool = False) -> None:
    """Clear the output directory, then write the layout's SVGs, index.json, and README.md."""
    output.clear(out, OURS, LEAD)
    for target, text in laid.files.items():
        (out / target).parent.mkdir(parents=True, exist_ok=True)
        (out / target).write_text(text)
    index = {"symbols": laid.symbols, "dropped": laid.dropped}
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    (out / "README.md").write_text(markdown(laid.rows, horizontal))


def symbols(
    out: Path,
    symbol_names: list[str] | None = None,
    model_identifiers: list[str] | None = None,
    horizontal: bool = False,
    secondary: float = HIERARCHY[1],
    tertiary: float = HIERARCHY[2],
) -> str:
    """Write the symbol of every device type, of the given symbols, or of the given model identifiers, into out; return a summary line.

    Symbols are written under their current names; a legacy symbol name, declared by a type or given, is followed to
    its current one. horizontal lays README.md's table out with a column per model identifier. secondary and tertiary
    are the opacities of layers at those levels.

    Exits before writing if a given symbol name is not in CoreGlyphs.bundle, or a given model identifier is not
    declared, resolves to no type, or gets no symbol, naming the identifier under the reason.
    """
    declarations = coretypes.read(coretypes.BUNDLE)
    known = sorted({name for declaration in declarations.values() for name in declaration.model_identifiers})
    if unknown := [name for name in model_identifiers or [] if name not in known]:
        sys.exit(f"not declared in {coretypes.BUNDLE}: {', '.join(unknown)}")
    resolved = declared(launchservices.preferred_type_identifiers(model_identifiers or known), declarations)
    chosen = {winner for winner in resolved.values() if winner is not None}
    declared_names = {type_identifier: coretypes.inherit(declarations[type_identifier], declarations).symbol_name for type_identifier in chosen}
    names = {type_identifier: coreglyphs.current(name) if name is not None else None for type_identifier, name in declared_names.items()}
    given = {name: coreglyphs.current(name) for name in symbol_names or []}
    needed = set(given.values()) if given else {name for name in names.values() if name is not None}
    outlines = {name: coreglyphs.outline(name) for name in sorted(needed)}
    if missing := [name for name, current_name in given.items() if outlines[current_name] is None]:
        sys.exit(f"no symbol in {coreglyphs.CATALOG}: {', '.join(missing)}")
    if given:
        names = {type_identifier: name for type_identifier, name in names.items() if name in needed}
        resolved = {model_identifier: winner for model_identifier, winner in resolved.items() if winner in names}
    laid = layout(names, resolved, outlines, list(given.values()), (HIERARCHY[0], secondary, tertiary))
    if model_identifiers and any(laid.dropped.values()):
        where = {"no symbol": coreglyphs.CATALOG}
        sys.exit("\n".join(f"{reason} in {where.get(reason, coretypes.BUNDLE)}: {', '.join(names)}" for reason, names in laid.dropped.items() if names))
    write(out, laid, horizontal)
    placed = sum(len(entry["model_identifiers"]) for entry in laid.symbols.values())
    dropped = ", ".join(f"{len(identifiers)} {reason}" for reason, identifiers in laid.dropped.items())
    return f"{len(resolved)} model identifiers: {placed} placed under {len(laid.symbols)} symbols in {out}; {dropped}"
