#!/usr/bin/env bash
grim -g "$(slurp)" - | swappy -f - -o - | wl-copy --type image/png && notify-send "Screenshot copied"

