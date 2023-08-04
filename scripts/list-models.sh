#!/usr/bin/env bash

while IFS= read -r -d '' file; do
    printf '\e[1m%s\e[0m\n' "$file"
    ./list-models.py "$file" | sed 's/^/    /'
done < <(find /System/Library/CoreServices -name "*.bundle" -print0)

#./list-models.py
