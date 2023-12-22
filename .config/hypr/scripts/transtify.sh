#!/usr/bin/env bash
transout=$(trans -b :zh "$(wl-paste)")
notify-send -- "$transout"
