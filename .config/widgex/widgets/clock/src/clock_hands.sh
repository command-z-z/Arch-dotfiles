#!/bin/sh
h=$(date +%-I)
m=$(date +%-M)
s=$(date +%-S)
printf '{"hour":"%s","minute":"%s","second":"%s"}\n' \
  "$(( (h % 12) * 30 + m / 2 ))" \
  "$(( m * 6 + s / 10 ))" \
  "$(( s * 6 ))"
