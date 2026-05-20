#!/usr/bin/env python3
"""
Pet brain: pet walks left/right, bounces at screen edges, occasionally idles.
Reacts to Claude Code state written to /tmp/widgex-pet-claude:
  tool_use → excited fast run
  done     → waving for ~2 s
  idle     → resume normal behaviour
Outputs JSON lines: {"row": "N", "count": "N", "x": "N", "y": "N"}
"""
import json, time, random, subprocess

FRAME_W = 192
FRAME_H = 208
BOTTOM_MARGIN = 24
CLAUDE_STATE_FILE = "/tmp/widgex-pet-claude"

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

def read_claude_state():
    try:
        return open(CLAUDE_STATE_FILE).read().strip()
    except Exception:
        return "idle"

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

# Claude state tracking
prev_claude = "idle"
wave_ticks  = 0   # countdown for post-tool waving
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

    claude = read_claude_state()

    # ── Detect transition: Claude turn ended → wave ───────────────────
    if claude == "done" and prev_claude != "done":
        wave_ticks = 30  # 3 s of waving
    prev_claude = claude

    # ── Claude-override state ─────────────────────────────────────────
    if wave_ticks > 0:
        state = STATE_WAVE
        wave_ticks -= 1
        # x keeps moving slowly while waving
        x += (speed * 0.4) * direction
        x = max(0.0, min(float(MAX_X), x))
    elif claude == "tool_use":
        # Excited fast run in current direction
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

    print(json.dumps({**state, "x": str(int(x)), "y": str(DRAW_Y)}), flush=True)
    time.sleep(0.1)
