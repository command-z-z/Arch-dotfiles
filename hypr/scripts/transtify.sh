#!/usr/bin/env bash
transout=$(trans -b :zh "$(wl-paste -p)")
notify-send -- "$transout"
