#!/usr/bin/env python3
import os
import plistlib
import sys
from contextlib import suppress


def print_models(bundle):
    info = "%s/Contents/Info.plist" % bundle
    if not os.path.exists(info):
        return

    props = plistlib.load(open(info, "rb"))
    if 'UTExportedTypeDeclarations' not in props:
        return

    models = []
    for exportedTypeDeclaration in props['UTExportedTypeDeclarations']:
        with suppress(KeyError):
            model = exportedTypeDeclaration['UTTypeTagSpecification']['com.apple.device-model-code']
            if isinstance(model, str):
                models.append(model)
            else:
                models.extend(model)
    fmt = ""
    i = 4
    models.sort()
    if len(models) > 1:
        prev = models[0][:i]
    else:
        prev = ""

    for model in models:
        if prev != (prev := model[:i]):
            fmt += "\n\n"
        fmt += f"{model}, "

    print(fmt)


def main():
    bundle = sys.argv[1] if len(sys.argv) > 1 else "/System/Library/CoreServices/CoreTypes.bundle"
    print_models(bundle)


if __name__ == "__main__":
    main()
