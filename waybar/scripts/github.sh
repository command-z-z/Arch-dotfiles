#!/bin/bash

NOTIFICATIONS="$(gh api notifications)"
COUNT="$(echo "$NOTIFICATIONS" | jq 'length')"

# echo '{"text": '$COUNT',"tooltip": "'$COUNT' Notifications"}'
echo '{"text": 0,"tooltip": "0 Notifications"}'
