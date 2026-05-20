#!/usr/bin/env python3
import json
import time
from pathlib import Path


STALE_AFTER_SECONDS = 300
DONE_VISIBLE_SECONDS = 3
CLAUDE_EVENT_FILE = Path("/tmp/widgex-agent-claude.json")
CODEX_EVENT_FILE = Path("/tmp/widgex-agent-codex.json")


COLORS = {
    "working": "var(--ctp-sapphire)",
    "active": "var(--ctp-yellow)",
    "done": "var(--ctp-green)",
    "idle": "var(--ctp-overlay1)",
    "error": "var(--ctp-red)",
}

SCORES = {
    "working": 90,
    "active": 64,
    "done": 100,
    "idle": 12,
    "error": 72,
}

LABELS = {
    "working": "Working",
    "active": "Active",
    "done": "Done",
    "idle": "Idle",
    "error": "Error",
}


def age_label(ts):
    if not ts:
        return "never"
    age = max(0, int(time.time() - ts))
    if age < 60:
        return f"{age}s ago"
    if age < 3600:
        return f"{age // 60}m ago"
    return f"{age // 3600}h ago"


def read_event(path):
    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(event, dict):
        return None
    return event


def normalize_state(raw):
    state = str(raw or "idle").lower()
    if state in {"tool_use", "tool-use", "tooluse"}:
        return "working"
    if state in {"working", "active", "done", "idle", "error"}:
        return state
    return "idle"


def agent_state(name, path):
    event = read_event(path)
    if not event:
        return "Idle", "no hook event", COLORS["idle"], SCORES["idle"], 0

    ts = float(event.get("ts") or 0)
    state = normalize_state(event.get("state"))
    if not ts or time.time() - ts > STALE_AFTER_SECONDS:
        return "Idle", "hook stale", COLORS["idle"], 18, ts

    age = time.time() - ts
    if state == "done" and age > DONE_VISIBLE_SECONDS:
        return "Idle", "hook idle", COLORS["idle"], 18, ts

    detail = str(event.get("detail") or event.get("event") or "hook event")
    return LABELS[state], detail, COLORS[state], SCORES[state], ts


def primary_state(claude, codex):
    c_state, c_detail, c_color, c_score, c_ts = claude
    x_state, x_detail, x_color, x_score, x_ts = codex

    if c_state == "Working":
        return "Claude Working", c_detail, c_color, c_score, c_ts
    if x_state == "Working":
        return "Codex Working", x_detail, x_color, x_score, x_ts
    if x_state == "Active":
        return "Codex Active", x_detail, x_color, x_score, x_ts
    if c_state == "Active":
        return "Claude Active", c_detail, c_color, c_score, c_ts
    if c_state == "Done":
        return "Claude Done", c_detail, c_color, c_score, c_ts
    if x_state == "Done":
        return "Codex Done", x_detail, x_color, x_score, x_ts
    return "All Quiet", "no active hook signal", COLORS["idle"], 8, max(c_ts, x_ts)


def main():
    claude = agent_state("Claude", CLAUDE_EVENT_FILE)
    codex = agent_state("Codex", CODEX_EVENT_FILE)
    primary, detail, color, score, last_ts = primary_state(claude, codex)

    payload = {
        "title": "AI Agent",
        "primary": primary,
        "primary_detail": detail,
        "status": primary.split(" ", 1)[-1],
        "accent_style": f"--agent-color: {color}; --agent-score: {score}%;",
        "dot_style": f"color: {color};",
        "bar_style": f"--agent-color: {color}; --agent-score: {score}%;",
        "claude_state": claude[0],
        "claude_detail": claude[1],
        "claude_style": f"color: {claude[2]};",
        "claude_bar_style": f"--agent-color: {claude[2]}; --agent-score: {claude[3]}%;",
        "codex_state": codex[0],
        "codex_detail": codex[1],
        "codex_style": f"color: {codex[2]};",
        "codex_bar_style": f"--agent-color: {codex[2]}; --agent-score: {codex[3]}%;",
        "source": "hooks + event parse",
        "updated": age_label(last_ts),
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
