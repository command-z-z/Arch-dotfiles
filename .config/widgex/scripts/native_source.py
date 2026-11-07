#!/usr/bin/env python3
"""Scoped JSON adapter and safe native preview sources (standard library only)."""
import argparse
import json
import math
import re
import subprocess
import sys

PALETTE = dict(zip(
    'rosewater flamingo pink mauve red maroon peach yellow green teal sky sapphire blue lavender text subtext1 subtext0 overlay2 overlay1 overlay0 surface2 surface1 surface0 base mantle crust'.split(),
    '#f2d5cf #eebebe #f4b8e4 #ca9ee6 #e78284 #ea999c #ef9f76 #e5c890 #a6d189 #81c8be #99d1db #85c1dc #8caaee #babbf1 #c6d0f5 #b5bfe2 #a5adce #949cbb #838ba7 #737994 #626880 #51576d #414559 #303446 #292c3c #232634'.split()))


def colors(text):
    return re.sub(r'var\(--ctp-([\w]+)\)', lambda m: PALETTE.get(m[1], '#838ba7'), text)


def adapt(payload):
    out = dict(payload)
    for key, value in payload.items():
        if not isinstance(value, str):
            continue
        if key.endswith('_color'):
            out[key] = colors(value)
        elif key.endswith('_style'):
            value = colors(value)
            color = re.search(r'--agent-color:\s*([^;]+)', value)
            score = re.search(r'--agent-score:\s*([\d.]+)', value)
            if color:
                out[key + '_color'] = color[1]
                out[key + '_score'] = score[1] if score else '0'
                value = f'color: {color[1]}; border-color: {color[1]};'
            out[key] = value
    # Do not draw synthetic forecast ranges when the original reports a failure.
    if payload.get('condition') == 'Weather unavailable':
        for i in range(1, 6):
            out[f'day{i}_bar_start'] = out[f'day{i}_bar_end'] = '0'
    return out


def finite(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else 0.0
    except (ValueError, TypeError):
        return 0.0


def progress_values(position, length):
    duration = max(0, finite(length) / 1_000_000)
    elapsed = min(duration, max(0, finite(position)))
    def clock(seconds):
        return f'{int(seconds) // 60:02}:{int(seconds) % 60:02}'
    return {'progress': f'{elapsed / duration * 100:g}' if duration else '0',
            'position': clock(elapsed), 'length': clock(duration)}


def seek_seconds(percent, length):
    try:
        percent = float(percent)
    except (ValueError, TypeError):
        return None
    duration = finite(length) / 1_000_000
    if not math.isfinite(percent) or not 0 <= percent <= 100 or duration <= 0:
        return None
    return duration * percent / 100


def playerctl(*args):
    try:
        return subprocess.check_output(['playerctl', '-p', 'spotify', *args], text=True,
                                       stderr=subprocess.DEVNULL, timeout=2).strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def music():
    status = playerctl('status')
    out = progress_values(playerctl('position') if status else '',
                          playerctl('metadata', 'mpris:length') if status else '')
    out.update(play_icon='󰏥' if status == 'Playing' else '󰐌',
               shuffle_icon='󰒟' if playerctl('shuffle') == 'On' else '󰒞',
               loop_icon={'Track': '󰑘', 'Playlist': '󰑖'}.get(playerctl('loop'), '󰕇'))
    return out


def notification_status(payload):
    """Normalize swaync subscription events without reading notification contents."""
    count = max(0, int(payload.get('count', 0)))
    dnd = payload.get('dnd') is True
    inhibited = payload.get('inhibited') is True
    icon = '󰂛' if dnd else ('󰵙' if inhibited and count else '󰂚')
    return {'text': f"{'' if dnd else ''} {count}", 'count': count, 'dnd': dnd,
            'icon': icon, 'indicator': '',
            'indicator_style': 'color: #f38ba8;' if count else 'color: #6c7086;'}


def notification_preview():
    out = {'dnd_label': 'Off · sample', 'dnd_style': '', 'volume_pct': '50'}
    for i in range(1, 21):
        out.update({f'notif_{i}_{key}': value for key, value in {
            'display': 'block' if i <= 2 else 'none', 'app': 'Native preview',
            'title': f'Sample notification {i}',
            'body': 'Appearance preview only. Existing swaync continues handling real notifications.',
            'time': 'sample', 'urgent_style': 'border-color: #ed8796;' if i == 2 else ''}.items()})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['json', 'music', 'seek', 'notifications', 'notifications-live'])
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()
    if args.mode == 'notifications-live':
        for line in sys.stdin:
            try:
                print(json.dumps(notification_status(json.loads(line)), ensure_ascii=False), flush=True)
            except (ValueError, TypeError, AttributeError):
                print('Invalid swaync status event', file=sys.stderr)
    elif args.mode == 'json':
        for line in sys.stdin:
            print(json.dumps(adapt(json.loads(line)), ensure_ascii=False), flush=True)
    elif args.mode == 'seek':
        position = seek_seconds(args.args[0] if args.args else '', playerctl('metadata', 'mpris:length'))
        if position is not None:
            playerctl('position', f'{position:.3f}')
    else:
        print(json.dumps(music() if args.mode == 'music' else notification_preview(), ensure_ascii=False))


if __name__ == '__main__':
    main()
