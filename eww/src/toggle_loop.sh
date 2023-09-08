#!/bin/bash

# 获取Spotify的循环状态
loop_status=$(playerctl -p spotify loop)

# 如果当前状态是"None"，则设置为"Track"，否则设置为"None"
if [ "$loop_status" = "None" ]; then
    playerctl -p spotify loop 'Track'
else
    playerctl -p spotify loop 'None'
fi

