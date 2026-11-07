#!/bin/bash

loop_status=$(playerctl -p spotify loop)

case "$loop_status" in
    None)
        playerctl -p spotify loop Track ;;
    Track)
        playerctl -p spotify loop Playlist ;;
    Playlist)
        playerctl -p spotify loop None ;;
    *)
        playerctl -p spotify loop None ;;
esac
