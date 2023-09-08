#!/bin/bash

# 获取Spotify歌曲长度（以微秒为单位）
length_microseconds=$(playerctl -p spotify metadata --format "{{ mpris:length }}")

# 将输入参数转换为小数
percentage=$1

# 计算歌曲的位置（以秒为单位）
position_seconds=$(echo "scale=2; $length_microseconds * $percentage / 100000000" | bc)

playerctl position $position_seconds
