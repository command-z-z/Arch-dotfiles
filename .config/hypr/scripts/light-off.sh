#!/usr/bin/env bash
liquidctl --match kraken set lcd screen brightness 0
liquidctl --match kraken set external color fixed 000000
/usr/bin/openrgb -p ~/.config/OpenRGB/off.orp

