#!/bin/bash

PATH=~/myConfig/Arch-dotfiles/wallpaper
# Get random image file name
IMG_NAME=$(/usr/bin/ls $PATH | /usr/bin/shuf -n 1)
# full path to that random image file
IMG_PATH=$PATH/$IMG_NAME
# Command to change wallpaper
/usr/bin/hyprctl hyprpaper wallpaper "DP-1,$IMG_PATH"  
