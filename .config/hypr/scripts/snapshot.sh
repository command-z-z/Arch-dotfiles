#!/usr/bin/env bash
grim -g "$(slurp)" - | swappy -f - && notify-send "Screenshot taken successfully"

