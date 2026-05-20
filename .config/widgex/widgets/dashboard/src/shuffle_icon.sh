#!/bin/bash

status=$(playerctl -p spotify shuffle 2>/dev/null)

if [[ "$status" == "Off" ]]; then
  printf "󰒞"
else
  printf "󰒟"
fi
