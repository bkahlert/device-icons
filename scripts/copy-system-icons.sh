#!/usr/bin/env bash

DESTINATION=$1

if [ -z "$DESTINATION" ]; then
    DESTINATION="$PWD/icns"
    mkdir -p "$DESTINATION" >/dev/null 2>&1 || { printf "\e[31mERROR: Failed to create \e[3m%s\e[23m.\e[0m\n" "$DESTINATION" >&2 && exit 1; }
fi

[ -d "$DESTINATION" ] || { printf "\e[31mERROR: The destination \e[3m%s\e[23m is no directory.\e[0m\n" "$DESTINATION" >&2 && exit 1; }

find /System/Library -type f -regex '.*\.icns' -exec cp {} "$DESTINATION"/ \;

for icns in "$DESTINATION"/*.icns; do
    name=$(basename "$icns" .icns)
    iconset_dir="$DESTINATION/$name.iconset"
    mkdir -p "$iconset_dir"
    iconutil -c iconset -o "$iconset_dir" "$icns"
done
