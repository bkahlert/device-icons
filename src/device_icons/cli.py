"""Command line of device-icons: dump and preview."""

from __future__ import annotations

import argparse
import sys


def parser() -> argparse.ArgumentParser:
    """Return the argument parser with the dump and preview commands."""
    root = argparse.ArgumentParser(prog="device-icons", description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("dump", help="write the icons and sidebar icons of device types")
    commands.add_parser("preview", help="show model identifiers as devices in Finder's Network view")
    return root


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    parser().parse_args(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
