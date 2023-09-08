#!/bin/bash

# 获取当前播放位置
dividend=$(playerctl metadata --format "{{ position }}")

# 获取歌曲长度
divisor=$(playerctl metadata --format "{{ mpris:length }}")

# # 计算百分比
result=$(echo "scale=2; $dividend / $divisor * 100" | bc)

echo $result

