#!/usr/bin/env bash

DESTINATION=$1

if [ -z "$DESTINATION" ]; then
    DESTINATION="$PWD/icns"
    mkdir -p "$DESTINATION" >/dev/null 2>&1 || { printf "\033[31mERROR: Failed to create \033[3m%s\033[23m.\033[0m\n" "$DESTINATION" >&2 && exit 1; }
fi

[ -d "$DESTINATION" ] || { printf "\033[31mERROR: The destination \033[3m%s\033[23m is no directory.\033[0m\n" "$DESTINATION" >&2 && exit 1; }

find /System/Library -type f -regex '.*\.icns' -exec cp {} "$DESTINATION"/ \;

for icns in "$DESTINATION"/*.icns; do
    name=$(basename "$icns" .icns)
    iconset_dir="$DESTINATION/$name.iconset"
    mkdir -p "$iconset_dir"
    iconutil -c iconset -o "$iconset_dir" "$icns"
done
