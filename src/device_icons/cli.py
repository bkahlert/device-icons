"""Command line of device-icons: dump, preview, and symbols."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from device_icons import dump, finder, preview, symbols


def parser() -> argparse.ArgumentParser:
    """Return the argument parser with the dump, preview, and symbols commands."""
    root = argparse.ArgumentParser(prog="device-icons", description="The Finder icons and SF Symbols of Apple device types.")
    commands = root.add_subparsers(dest="command", required=True)
    dumping = commands.add_parser("dump", help="write the icon and sidebar icon of every device type, grouped for picking in Finder")
    dumping.add_argument("out", nargs="?", type=Path, default=Path("out"), help="output directory, emptied first (default: out)")
    only = dumping.add_mutually_exclusive_group()
    only.add_argument(
        "--type",
        dest="type_identifiers",
        metavar="TYPE_IDENTIFIER",
        action="append",
        help="dump only this type identifier, with the model identifiers that resolve to it; repeatable",
    )
    only.add_argument(
        "--model",
        dest="model_identifiers",
        metavar="MODEL_IDENTIFIER",
        action="append",
        help="dump only this model identifier, with the type it resolves to; repeatable",
    )
    dumping.add_argument("--no-open", dest="open", action="store_false", help="do not open the output directory in Finder")
    dumping.add_argument("--horizontal", action="store_true", help="lay README.md's table out with a column per model identifier")
    symbolling = commands.add_parser("symbols", help="write the SF Symbol of every device type as SVG, with the model identifiers that get it")
    symbolling.add_argument("out", nargs="?", type=Path, default=Path("out"), help="output directory, emptied first (default: out)")
    symbolling.add_argument(
        "--symbol",
        dest="symbol_names",
        metavar="SYMBOL_NAME",
        action="append",
        help="write only this symbol, with the model identifiers that get it; repeatable, any SF Symbol",
    )
    symbolling.add_argument("--no-open", dest="open", action="store_false", help="do not open the output directory in Finder")
    symbolling.add_argument("--horizontal", action="store_true", help="lay README.md's table out with a column per model identifier")
    previewing = commands.add_parser("preview", help="show model identifiers as devices in Finder's Network view until Ctrl-C")
    previewing.add_argument("model_identifiers", metavar="MODEL_IDENTIFIER", nargs="+", help="a model identifier, such as MacPro7,1")
    previewing.add_argument("--name", help="service instance name Finder shows (default: the model identifier)")
    previewing.add_argument("--no-open", dest="open", action="store_false", help="do not open Finder's Network view")
    previewing.set_defaults(command_parser=previewing)
    return root


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    arguments = parser().parse_args(argv)
    if sys.platform != "darwin":
        sys.exit("macOS only: needs CoreTypes.bundle, CoreGlyphs.bundle, iconutil, osascript, and dns-sd")
    if arguments.command == "dump":
        print(dump.dump(arguments.out, arguments.type_identifiers, arguments.model_identifiers, arguments.horizontal))
        if arguments.open:
            finder.show(arguments.out)
    elif arguments.command == "symbols":
        print(symbols.symbols(arguments.out, arguments.symbol_names, arguments.horizontal))
        if arguments.open:
            finder.show(arguments.out)
    else:
        try:
            commands = preview.registrations(arguments.model_identifiers, arguments.name)
        except ValueError as error:
            arguments.command_parser.error(str(error))
        if arguments.open:
            finder.show(finder.NETWORK_VIEW)
        preview.preview(commands)
    return 0


if __name__ == "__main__":
    sys.exit(main())
