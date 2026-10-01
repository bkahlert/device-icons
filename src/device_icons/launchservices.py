"""The preferred type identifier of a model identifier, asked of LaunchServices the way Finder asks."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable

from device_icons.coretypes import MODEL_IDENTIFIER_TAG_CLASS

# JavaScript for Automation. Finder only takes devices: a display's model identifier, whose type conforms to
# public.display, gets a question mark in Network, so public.device is the type to conform to.
PREFERRED_TYPE_IDENTIFIERS = f"""
ObjC.import('CoreServices');
function run(argv) {{
  return argv.map(modelIdentifier => {{
    const ref = $.UTTypeCreatePreferredIdentifierForTag($('{MODEL_IDENTIFIER_TAG_CLASS}'), $(modelIdentifier), $('public.device'));
    return modelIdentifier + '\\t' + ObjC.castRefToObject(ref).js;
  }}).join('\\n');
}}
"""


def preferred_type_identifiers(model_identifiers: list[str]) -> dict[str, str]:
    """Return the preferred type identifier of each model identifier; a dynamic dyn.* type for one no type claims."""
    if not model_identifiers:
        return {}
    command = ["osascript", "-l", "JavaScript", "-e", PREFERRED_TYPE_IDENTIFIERS, *model_identifiers]
    out = subprocess.run(command, check=True, capture_output=True, text=True).stdout
    return dict(line.split("\t") for line in out.splitlines() if line)


def declared(preferred: dict[str, str], declarations: Iterable[str]) -> dict[str, str | None]:
    """Return each model identifier's preferred type identifier as declared, or None where no declaration matches.

    Type identifiers are case-insensitive: LaunchServices returns them lowercased, the bundle declares some with capitals.
    """
    by_lower = {name.lower(): name for name in declarations}
    return {model_identifier: by_lower.get(winner.lower()) for model_identifier, winner in preferred.items()}
