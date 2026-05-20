#!/bin/bash

status=$(playerctl -p spotify status 2>/dev/null)

if [[ "$status" == "Playing" ]]; then
  printf ""
else
  printf ""
fi
