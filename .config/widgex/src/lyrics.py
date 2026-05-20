#!/usr/bin/env python3

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PLAYER = "spotify"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "widgex"
CACHE_DIR = CONFIG_DIR / "spotify_cache" / "lyrics"
LYRIC_RE = re.compile(r"^\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\]\s*(.*)$")


def print_lyrics(current="", next_line=""):
    print(
        json.dumps(
            {
                "current": current,
                "next": next_line,
            },
            ensure_ascii=False,
        )
    )


def playerctl(*args):
    try:
        result = subprocess.run(
            ["playerctl", "-p", PLAYER, *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
    except Exception:
        return ""
    return result.stdout.strip()


def cache_key(*parts):
    return hashlib.sha1("\0".join(parts).encode("utf-8")).hexdigest()


def fetch_synced_lyrics(title, artist, album, duration):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{cache_key(artist, title, album, duration)}.lrc"

    if path.exists():
        return path.read_text(encoding="utf-8")

    query = {
        "track_name": title,
        "artist_name": artist,
        "album_name": album,
    }
    if duration.isdigit() and int(duration) > 0:
        query["duration"] = str(round(int(duration) / 1_000_000))

    url = "https://lrclib.net/api/get?" + urlencode(query)
    request = Request(url, headers={"User-Agent": "eww-spotify-lyrics/1.0"})

    try:
        with urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return ""

    lyrics = data.get("syncedLyrics") or ""
    path.write_text(lyrics, encoding="utf-8")
    return lyrics


def parse_timestamp(minutes, seconds, fraction):
    total = int(minutes) * 60 + int(seconds)
    if fraction:
        total += int(fraction.ljust(3, "0")[:3]) / 1000
    return total


def parse_lyrics(lyrics):
    lines = []

    for raw_line in lyrics.splitlines():
        match = LYRIC_RE.match(raw_line)
        if not match:
            continue

        timestamp = parse_timestamp(match.group(1), match.group(2), match.group(3))
        line = match.group(4).strip()
        if line:
            lines.append((timestamp, line))

    return lines


def lyric_window(lyrics, position):
    lines = parse_lyrics(lyrics)
    if not lines:
        return "", ""

    current_index = -1
    for index, (timestamp, _line) in enumerate(lines):
        if timestamp <= position:
            current_index = index
        else:
            break

    if current_index < 0:
        return "", lines[0][1]

    current = lines[current_index][1]
    next_line = lines[current_index + 1][1] if current_index + 1 < len(lines) else ""
    return current, next_line


def main():
    if not playerctl("status"):
        print_lyrics()
        return

    title = playerctl("metadata", "xesam:title")
    artist = playerctl("metadata", "xesam:artist")
    album = playerctl("metadata", "xesam:album")
    duration = playerctl("metadata", "mpris:length")
    position = playerctl("position")

    if not title or not artist:
        print_lyrics()
        return

    try:
        position_seconds = float(position)
    except ValueError:
        print_lyrics()
        return

    lyrics = fetch_synced_lyrics(title, artist, album, duration)
    current, next_line = lyric_window(lyrics, position_seconds)
    print_lyrics(current, next_line)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
