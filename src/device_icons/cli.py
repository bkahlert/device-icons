"""Command line of device-icons: icons export, icons preview, and symbols export."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from device_icons import coreglyphs, finder, icons, preview, symbols


def parser() -> argparse.ArgumentParser:
    """Return the argument parser with the icons and symbols commands and their actions."""
    root = argparse.ArgumentParser(prog="device-icons", description="The Finder icons and SF Symbols of Apple device types.")
    commands = root.add_subparsers(dest="command", required=True)
    iconing = commands.add_parser("icons", help="the icon and sidebar icon Finder draws for a device type")
    icon_actions = iconing.add_subparsers(dest="action", required=True)
    writing = icon_actions.add_parser("export", help="export the icon and sidebar icon of every device type, grouped for picking in Finder")
    writing.add_argument("out", nargs="?", type=Path, default=Path("out"), help="output directory, emptied first (default: out)")
    only = writing.add_mutually_exclusive_group()
    only.add_argument(
        "--type",
        dest="type_identifiers",
        metavar="TYPE_IDENTIFIER",
        action="append",
        help="export only this type identifier, with the model identifiers that resolve to it; repeatable",
    )
    only.add_argument(
        "--model",
        dest="model_identifiers",
        metavar="MODEL_IDENTIFIER",
        action="append",
        help="export only this model identifier, with the type it resolves to; repeatable",
    )
    writing.add_argument("--no-open", dest="open", action="store_false", help="do not open the output directory in Finder")
    writing.add_argument("--horizontal", action="store_true", help="lay README.md's table out with a column per model identifier")
    previewing = icon_actions.add_parser("preview", help="show model identifiers as devices in Finder's Network view until Ctrl-C")
    previewing.add_argument("model_identifiers", metavar="MODEL_IDENTIFIER", nargs="+", help="a model identifier, such as MacPro7,1")
    previewing.add_argument("--name", help="service instance name Finder shows (default: the model identifier)")
    previewing.add_argument("--no-open", dest="open", action="store_false", help="do not open Finder's Network view")
    previewing.set_defaults(command_parser=previewing)
    symbolling = commands.add_parser("symbols", help="the SF Symbol of a device type")
    symbol_actions = symbolling.add_subparsers(dest="action", required=True)
    drawing = symbol_actions.add_parser("export", help="export the SF Symbol of every device type as SVG, with the model identifiers that get it")
    drawing.add_argument("out", nargs="?", type=Path, default=Path("out"), help="output directory, emptied first (default: out)")
    some = drawing.add_mutually_exclusive_group()
    some.add_argument(
        "--symbol",
        dest="symbol_names",
        metavar="SYMBOL_NAME",
        action="append",
        help="export only this symbol, with the model identifiers that get it; repeatable, any SF Symbol",
    )
    some.add_argument(
        "--model",
        dest="model_identifiers",
        metavar="MODEL_IDENTIFIER",
        action="append",
        help="export only the symbol of this model identifier, with this model identifier; repeatable",
    )
    drawing.add_argument(
        "--secondary",
        type=opacity,
        default=coreglyphs.HIERARCHY[1],
        metavar="OPACITY",
        help="opacity of a secondary layer, 0 to 1 (default: %(default)s, as AppKit draws it)",
    )
    drawing.add_argument(
        "--tertiary",
        type=opacity,
        default=coreglyphs.HIERARCHY[2],
        metavar="OPACITY",
        help="opacity of a tertiary layer, 0 to 1 (default: %(default)s, as AppKit draws it)",
    )
    drawing.add_argument("--no-open", dest="open", action="store_false", help="do not open the output directory in Finder")
    drawing.add_argument("--horizontal", action="store_true", help="lay README.md's table out with a column per model identifier")
    return root


def opacity(text: str) -> float:
    """Return the opacity text gives; raise ArgumentTypeError if it is not a number between 0 and 1."""
    value = float(text)
    if not 0 <= value <= 1:
        raise argparse.ArgumentTypeError(f"{text} is not between 0 and 1")
    return value


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    arguments = parser().parse_args(argv)
    if sys.platform != "darwin":
        sys.exit("macOS only: needs CoreTypes.bundle, CoreGlyphs.bundle, iconutil, osascript, and dns-sd")
    match arguments.command, arguments.action:
        case "icons", "export":
            print(icons.icons(arguments.out, arguments.type_identifiers, arguments.model_identifiers, arguments.horizontal))
            if arguments.open:
                finder.show(arguments.out)
        case "icons", "preview":
            try:
                commands = preview.registrations(arguments.model_identifiers, arguments.name)
            except ValueError as error:
                arguments.command_parser.error(str(error))
            if arguments.open:
                finder.show(finder.NETWORK_VIEW)
            preview.preview(commands)
        case "symbols", "export":
            print(
                symbols.symbols(
                    arguments.out,
                    arguments.symbol_names,
                    arguments.model_identifiers,
                    horizontal=arguments.horizontal,
                    secondary=arguments.secondary,
                    tertiary=arguments.tertiary,
                )
            )
            if arguments.open:
                finder.show(arguments.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
