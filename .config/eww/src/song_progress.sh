#!/bin/bash

dividend=$(playerctl metadata --format "{{ position }}")
pos=$((dividend/1000000))
cur_position=$(date -u -d@"$pos" +'%M:%S')

divisor=$(playerctl metadata --format "{{ mpris:length }}")
length=$((divisor/1000000))
total_length=$(date -u -d@"$length" +'%M:%S')

result=$(echo "scale=2; $dividend / $divisor * 100" | bc)

case $1 in
	progress)
		echo $result;;
	position)
		echo $cur_position ;;
	length)
		echo $total_length ;;
esac
