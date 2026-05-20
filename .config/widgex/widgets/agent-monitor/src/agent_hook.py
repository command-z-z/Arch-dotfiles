#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

EVENT_FILES = {
    "claude": Path("/tmp/widgex-agent-claude.json"),
    "codex": Path("/tmp/widgex-agent-codex.json"),
}
LEGACY_CLAUDE_FILE = Path("/tmp/widgex-pet-claude")

CODEX_STATE_BY_EVENT = {
    "SessionStart": ("active", "session start"),
    "UserPromptSubmit": ("active", "prompt submitted"),
    "PreToolUse": ("working", "pre tool use"),
    "PermissionRequest": ("working", "permission request"),
    "PostToolUse": ("working", "post tool use"),
    "Stop": ("done", "turn stop"),
}

CLAUDE_STATE_BY_EVENT = {
    "PreToolUse": ("working", "tool use hook"),
    "Stop": ("done", "stop hook"),
}


def read_payload():
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw.strip()}
    return data if isinstance(data, dict) else {}


def atomic_write(path, text):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def infer_state(agent, payload, explicit_state):
    event = str(payload.get("hook_event_name") or "manual")
    tool = payload.get("tool_name")
    if explicit_state:
        state = explicit_state
        detail = event if event != "manual" else state.replace("_", " ")
    elif agent == "codex":
        state, detail = CODEX_STATE_BY_EVENT.get(event, ("active", event))
    else:
        state, detail = CLAUDE_STATE_BY_EVENT.get(event, ("active", event))
    if tool:
        detail = f"{detail}: {tool}"
    return state, detail, event


def write_state(agent, state, detail, event, payload):
    event_path = EVENT_FILES[agent]
    output = {
        "agent": agent,
        "state": state,
        "event": event,
        "detail": detail,
        "ts": time.time(),
        "cwd": payload.get("cwd"),
        "session_id": payload.get("session_id"),
        "turn_id": payload.get("turn_id"),
    }
    atomic_write(event_path, json.dumps(output, ensure_ascii=False))

    if agent == "claude":
        legacy = "tool_use" if state in {"working", "tool_use"} else state
        if legacy not in {"tool_use", "done", "idle"}:
            legacy = "idle"
        atomic_write(LEGACY_CLAUDE_FILE, legacy + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", choices=sorted(EVENT_FILES))
    parser.add_argument("state", nargs="?")
    parser.add_argument("--delay-idle", type=float, default=0)
    args = parser.parse_args()

    payload = read_payload()
    state, detail, event = infer_state(args.agent, payload, args.state)
    write_state(args.agent, state, detail, event, payload)

    if args.delay_idle > 0:
        cmd = [sys.executable, __file__, args.agent, "idle"]
        subprocess.Popen(
            ["sh", "-c", f"sleep {args.delay_idle}; exec {cmd[0]} {cmd[1]} {cmd[2]} {cmd[3]}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    if event == "Stop":
        print('{"continue": true}')


if __name__ == "__main__":
    main()
