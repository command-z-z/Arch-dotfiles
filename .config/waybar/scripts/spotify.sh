#!/usr/bin/env bash

while true; do

	player_status=$(playerctl -p spotify status 2>/dev/null)

	if [ "$player_status" = "Playing" ] || [ "$player_status" = "Paused" ]; then
		artist=$(playerctl -p spotify metadata artist 2>/dev/null)
		title=$(playerctl -p spotify metadata title 2>/dev/null)
		album=$(playerctl -p spotify metadata album 2>/dev/null)

		if [ -n "$artist$title" ]; then
			pause_icon=""
			spotify_icon=""

			if [ "$player_status" = "Paused" ]; then
				pause_icon=" "
			fi

			if [ -n "$album" ]; then
				spotify_icon="<span color='#1db954'></span> "
			fi

			echo "${spotify_icon}${pause_icon}${artist} - ${title}"
		else
			echo ""
		fi
	else
		echo ""
	fi

	sleep 1

done
