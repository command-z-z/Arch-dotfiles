#!/usr/bin/env python3
"""Bottom-edge desktop pet with read-only Codex activity reactions.

Working: run faster; a completed observed turn: wave for three seconds;
interrupted: wait; offline/unknown: ordinary roaming. Emits animation JSONL.
"""
import json, time, random, subprocess
from codex_state import Tracker, Reaction

FRAME_W = 192
FRAME_H = 208
BOTTOM_MARGIN = 24

def get_screen_metrics():
    try:
        monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"]))
        m = max(monitors, key=lambda m: m["width"] * m["height"])
        w = m["width"]
        h = m["height"]
        # Hyprland reserved: [left, top, right, bottom].
        # The pet's absolute floor only follows bottom reserved space. Top reserved
        # is used only to compensate for the layer-shell surface origin moving down.
        reserved = m.get("reserved", [0, 0, 0, 0])
        return w, h, reserved[1], reserved[3]
    except Exception:
        return 1920, 1080, 0, 0

SCREEN_W, SCREEN_H, RESERVED_TOP, RESERVED_BOTTOM = get_screen_metrics()
MAX_X = SCREEN_W - FRAME_W
DRAW_Y = SCREEN_H - RESERVED_BOTTOM - FRAME_H - BOTTOM_MARGIN - RESERVED_TOP

STATE_RUN_RIGHT = {"row": "1", "count": "8"}
STATE_RUN_LEFT  = {"row": "2", "count": "8"}
STATE_WAVE      = {"row": "3", "count": "4"}
STATE_WAIT      = {"row": "6", "count": "6"}
IDLE_POOL = [
    {"row": "0", "count": "6"},
    {"row": "0", "count": "6"},
    {"row": "3", "count": "4"},
    {"row": "6", "count": "6"},
]

x          = float(random.randint(200, MAX_X - 200))
speed      = 5.0
direction  = random.choice([-1, 1])
is_idle    = False
idle_state = IDLE_POOL[0]
ticks_left = random.randint(30, 70)

# Codex status sampling is separate from the 10 FPS movement loop.
tracker = Tracker()
reaction = Reaction()
next_codex_poll = 0.0
metrics_ticks = 0

while True:
    if metrics_ticks <= 0:
        SCREEN_W, SCREEN_H, RESERVED_TOP, RESERVED_BOTTOM = get_screen_metrics()
        MAX_X = SCREEN_W - FRAME_W
        DRAW_Y = max(0, SCREEN_H - RESERVED_BOTTOM - FRAME_H - BOTTOM_MARGIN - RESERVED_TOP)
        x = max(0.0, min(float(MAX_X), x))
        metrics_ticks = 10
    else:
        metrics_ticks -= 1

    now = time.monotonic()
    if now >= next_codex_poll:
        reaction.accept(tracker.read(), now)
        next_codex_poll = now + 1.0
    mode = reaction.mode(now)

    if mode == "wave":
        state = STATE_WAVE
        x += (speed * 0.4) * direction
        x = max(0.0, min(float(MAX_X), x))
    elif mode == "waiting":
        state = STATE_WAIT
    elif mode == "running":
        run_speed = speed * 2.5
        x += run_speed * direction
        if x >= MAX_X:
            x = float(MAX_X); direction = -1
        elif x <= 0:
            x = 0.0; direction = 1
        state = STATE_RUN_RIGHT if direction > 0 else STATE_RUN_LEFT
    else:
        # ── Normal behaviour ──────────────────────────────────────────
        if is_idle:
            state = idle_state
            ticks_left -= 1
            if ticks_left <= 0:
                is_idle = False
                ticks_left = random.randint(30, 80)
        else:
            state = STATE_RUN_RIGHT if direction > 0 else STATE_RUN_LEFT
            x += speed * direction

            if x >= MAX_X:
                x = float(MAX_X)
                direction = -1
                is_idle = True
                idle_state = random.choice(IDLE_POOL)
                ticks_left = random.randint(10, 30)
            elif x <= 0:
                x = 0.0
                direction = 1
                is_idle = True
                idle_state = random.choice(IDLE_POOL)
                ticks_left = random.randint(10, 30)
            else:
                ticks_left -= 1
                if ticks_left <= 0:
                    is_idle = True
                    idle_state = random.choice(IDLE_POOL)
                    ticks_left = random.randint(20, 50)

    print(json.dumps({**state, "x": str(int(x)), "y": str(DRAW_Y), "codex_state": reaction.current[0], "mode": mode}), flush=True)
    time.sleep(0.1)
