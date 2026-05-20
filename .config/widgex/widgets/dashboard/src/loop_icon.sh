#!/bin/bash

status=$(playerctl -p spotify loop 2>/dev/null)

case "$status" in
  None)
    printf "󰕇"
    ;;
  Track)
    printf "󰑘"
    ;;
  *)
    printf "󰑖"
    ;;
esac
