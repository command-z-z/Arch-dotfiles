#!/bin/bash

loop_status=$(playerctl -p spotify loop)

if [ "$loop_status" = "None" ]; then
    playerctl -p spotify loop 'Track'
else
    playerctl -p spotify loop 'None'
fi

