#!/usr/bin/env python3
"""JSON source for the Widgex top bar."""
import json
import calendar
import socket
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import time


WORKSPACE_ICONS = {
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "󰢹",
    "6": "",
}

PACMAN_CACHE_FILE = os.path.expanduser("~/.cache/widgex/pacman-updates.json")
PACMAN_UPDATE_TTL_SECONDS = 15 * 60
GITHUB_CACHE_FILE = os.path.expanduser("~/.cache/widgex/github-notifications.json")
GITHUB_UPDATE_TTL_SECONDS = 5 * 60


def run(command, timeout=1.0):
    try:
        return subprocess.check_output(
            command,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
        ).strip()
    except Exception:
        return ""


def run_json(command, timeout=1.0):
    try:
        return json.loads(run(command, timeout))
    except Exception:
        return {}


def active_workspace_name():
    data = run_json(["hyprctl", "activeworkspace", "-j"])
    return str(data.get("name") or data.get("id") or "")


WORKSPACE_SLOTS = 32


def workspace_list():
    active = run_json(["hyprctl", "activeworkspace", "-j"])
    workspaces = run_json(["hyprctl", "workspaces", "-j"])
    monitor = active.get("monitor") if isinstance(active, dict) else None
    workspaces = workspaces if isinstance(workspaces, list) else []
    return sorted((w for w in workspaces if w.get("id", -1) > 0
                   and (not monitor or w.get("monitor") == monitor)), key=lambda w: w["id"])


def workspace_payload(urgent=None):
    urgent = urgent or set()
    active = active_workspace_name()
    workspaces = workspace_list()
    payload = {}
    for slot in range(1, WORKSPACE_SLOTS + 1):
        w = workspaces[slot - 1] if slot <= len(workspaces) else None
        name = str(w.get("name", w["id"])) if w else ""
        alarm = w is not None and w["id"] in urgent and name != active
        payload[f"workspace{slot}"] = "" if alarm else WORKSPACE_ICONS.get(name, "")
        payload[f"workspace{slot}_visible"] = "true" if w else "false"
        payload[f"workspace{slot}_style"] = ("background: #ed8796; color: #cad3f5;" if alarm
            else "color: #8aadf4;" if name == active else "")
    return payload


def workspace_stream():
    path = Path(os.environ["XDG_RUNTIME_DIR"]) / "hypr" / os.environ["HYPRLAND_INSTANCE_SIGNATURE"] / ".socket2.sock"
    urgent = set()
    events = ("workspace", "createworkspace", "destroyworkspace", "focusedmon", "moveworkspace", "urgent", "monitor")
    while True:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(str(path))
                print(json.dumps(workspace_payload(urgent), ensure_ascii=False), flush=True)
                with sock.makefile() as stream:
                    for line in stream:
                        event, _, value = line.strip().partition(">>")
                        if not event.startswith(events):
                            continue
                        if event == "urgent":
                            clients = run_json(["hyprctl", "clients", "-j"])
                            for c in clients if isinstance(clients, list) else []:
                                if str(c.get("address", "")).removeprefix("0x") == value.removeprefix("0x"):
                                    urgent.add(c.get("workspace", {}).get("id"))
                        active = run_json(["hyprctl", "activeworkspace", "-j"])
                        urgent.discard(active.get("id"))
                        print(json.dumps(workspace_payload(urgent), ensure_ascii=False), flush=True)
        except (OSError, KeyError, ValueError):
            time.sleep(1)


def focus_workspace_slot(slot):
    workspaces = workspace_list()
    if 1 <= slot <= len(workspaces):
        name = str(workspaces[slot - 1].get("name", workspaces[slot - 1]["id"]))
        subprocess.run(["hyprctl", "eval", "hl.dispatch(hl.dsp.focus({workspace=" + json.dumps(name) + "}))"], check=True)



def active_window():
    data = run_json(["hyprctl", "activewindow", "-j"])
    title = str(data.get("title") or "")
    klass = str(data.get("class") or "")
    if not title:
        return klass or "Desktop"
    rewrites = {
        "Google Chrome": "🌎 chrome",
        "Spotify": "🎼 spotify",
        "org.pwmt.zathura": "📰 zathura",
    }
    for needle, label in rewrites.items():
        if needle in title or needle in klass:
            return label
    return title


def spotify():
    status = run(["playerctl", "-p", "spotify", "status"], timeout=0.5)
    if status not in {"Playing", "Paused"}:
        return ""
    artist = run(["playerctl", "-p", "spotify", "metadata", "artist"], timeout=0.5)
    title = run(["playerctl", "-p", "spotify", "metadata", "title"], timeout=0.5)
    if not (artist or title):
        return ""
    paused = " " if status == "Paused" else ""
    text = " - ".join(part for part in [artist, title] if part)
    return f"{paused}{text}"


def cpu_percent():
    def read_cpu():
        values = [int(part) for part in open("/proc/stat", encoding="utf-8").readline().split()[1:]]
        idle = values[3] + values[4]
        total = sum(values)
        return idle, total

    try:
        idle1, total1 = read_cpu()
        time.sleep(0.08)
        idle2, total2 = read_cpu()
        total_delta = total2 - total1
        idle_delta = idle2 - idle1
        if total_delta <= 0:
            return " --%"
        return f" {round((1 - idle_delta / total_delta) * 100)}%"
    except Exception:
        return " --%"


def memory_percent():
    try:
        fields = {}
        for line in open("/proc/meminfo", encoding="utf-8"):
            key, value = line.split(":", 1)
            fields[key] = int(value.split()[0])
        total = fields["MemTotal"]
        available = fields["MemAvailable"]
        return f" {round((total - available) / total * 100)}%"
    except Exception:
        return " --%"


def disk_percent():
    try:
        usage = shutil.disk_usage("/")
        return f" {round(usage.used / usage.total * 100)}%"
    except Exception:
        return " --%"


def gpu_temp():
    output = run(
        [
            "nvidia-smi",
            "--query-gpu=temperature.gpu",
            "--format=csv,noheader,nounits",
        ],
        timeout=0.8,
    )
    temps = [part.strip() for part in output.splitlines() if part.strip()]
    if not temps:
        return " --°C"
    return f" {max(int(temp) for temp in temps if temp.isdigit())}°C"


def volume():
    output = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], timeout=0.5)
    if "MUTED" in output:
        return ""
    match = re.search(r"([0-9]*\.?[0-9]+)", output)
    if not match:
        return " --%"
    percent = round(float(match.group(1)) * 100)
    icon = "" if percent >= 50 else ""
    return f"{icon} {percent}%"


def network():
    output = run(["nmcli", "-t", "-f", "TYPE,STATE,CONNECTION", "device"], timeout=0.8)
    for line in output.splitlines():
        device_type, state, connection = (line.split(":", 2) + ["", "", ""])[:3]
        if state == "connected":
            if device_type == "wifi":
                return " "
            if device_type == "ethernet":
                return ""
    return " Disconnected"


def bluetooth():
    output = run(["bluetoothctl", "show"], timeout=0.5)
    if "Powered: yes" not in output:
        return ""
    devices = run(["bluetoothctl", "devices", "Connected"], timeout=0.5)
    count = len([line for line in devices.splitlines() if line.strip()])
    return f" {count}" if count else ""


def read_timed_cache(path):
    try:
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
        text = str(cached.get("text") or "")
        checked_at = float(cached.get("checked_at") or 0)
        return text, checked_at
    except Exception:
        return "", 0


def write_timed_cache(path, text):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"text": text, "checked_at": time.time()}, f)
    except Exception:
        pass


def github_notifications():
    cached_text, checked_at = read_timed_cache(GITHUB_CACHE_FILE)
    if cached_text and time.time() - checked_at < GITHUB_UPDATE_TTL_SECONDS:
        return cached_text

    output = run(["gh", "api", "notifications"], timeout=1.2)
    try:
        text = f" {len(json.loads(output))}"
    except Exception:
        text = cached_text or " --"
    write_timed_cache(GITHUB_CACHE_FILE, text)
    return text


def parse_updates_output(output):
    if not output:
        return "󰂪"
    try:
        data = json.loads(output)
        text = str(data.get("text") or "").strip()
        alt = str(data.get("alt") or "")
        icon = "󱍷" if "has-updates" in alt or text not in {"", "0"} else "󰂪"
        return f"{icon} {text}".strip()
    except Exception:
        return output.splitlines()[0][:16]


def updates():
    cached_text, checked_at = read_timed_cache(PACMAN_CACHE_FILE)
    if cached_text and time.time() - checked_at < PACMAN_UPDATE_TTL_SECONDS:
        return cached_text

    output = run(["waybar-module-pacman-updates"], timeout=3.0)
    if output:
        text = parse_updates_output(output)
        write_timed_cache(PACMAN_CACHE_FILE, text)
        return text

    fallback = cached_text or "󰂪"
    write_timed_cache(PACMAN_CACHE_FILE, fallback)
    return fallback


def notifications():
    status_file = os.path.expanduser("~/.cache/widgex/notif-status.json")
    try:
        with open(status_file) as f:
            data = json.load(f)
        count = int(data.get("count", 0))
        dnd = bool(data.get("dnd", False))
        icon = "" if dnd else ""
        text = str(count) if count > 0 else ""
        return f"{icon} {text}".strip()
    except Exception:
        return ""


CLOCK_ALT_FILE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "widgex" / "clock-alt"


def clock():
    if CLOCK_ALT_FILE.exists():
        return time.strftime("%Y-%m-%d")
    return time.strftime("%a %d, %b \n %I:%M %p")


def tooltips():
    now = time.localtime()
    cal = calendar.TextCalendar().formatmonth(now.tm_year, now.tm_mon).rstrip()
    devices = run(["nmcli", "-t", "-f", "DEVICE,STATE", "device"], timeout=1)
    device = next((line.split(":", 1)[0] for line in devices.splitlines()
                   if line.endswith(":connected")), "")
    details = run(["nmcli", "-f", "GENERAL.DEVICE,GENERAL.CONNECTION,IP4.ADDRESS,IP4.GATEWAY",
                   "device", "show", device], timeout=1) if device else "Not connected to a network"
    bt = run(["bluetoothctl", "devices", "Connected"], timeout=1) or "No connected Bluetooth devices"
    load = ", ".join(f"{n:.2f}" for n in os.getloadavg())
    return {"calendar": cal,
            "network": details,
            "bluetooth": bt,
            "cpu": f"CPU threads: {os.cpu_count()}\nLoad average (1 / 5 / 15 min): {load}"}


def main():
    if sys.argv[1:] == ["--workspaces-stream"]:
        workspace_stream()
        return
    if len(sys.argv) == 3 and sys.argv[1] == "--workspace-slot":
        focus_workspace_slot(int(sys.argv[2]))
        return
    if sys.argv[1:] == ["--tooltips"]:
        print(json.dumps(tooltips(), ensure_ascii=False), flush=True)
        return
    if sys.argv[1:] == ["--fast"]:
        print(json.dumps({"clock": clock(), "volume": volume()}, ensure_ascii=False), flush=True)
        return
    if sys.argv[1:] == ["--toggle-clock"]:
        if CLOCK_ALT_FILE.exists():
            CLOCK_ALT_FILE.unlink()
        else:
            CLOCK_ALT_FILE.parent.mkdir(parents=True, exist_ok=True)
            CLOCK_ALT_FILE.touch()
        return
    payload = {
        "launcher": "",
        "window": active_window(),
        "spotify": spotify(),
        "gpu": gpu_temp(),
        "cpu": cpu_percent(),
        "memory": memory_percent(),
        "disk": disk_percent(),
        "volume": volume(),
        "network": network(),
        "bluetooth": bluetooth(),
        "github": github_notifications(),
        "updates": updates(),
        "notifications": " preview",
        "clock": clock(),
    }
    payload["spotify_visible"] = "true" if payload["spotify"] else "false"
    payload["spotify_icon"] = "" if payload["spotify"] else ""
    # Old cache entries contain the previous update glyphs.
    payload["updates"] = payload["updates"].replace("", "󱍷").replace("", "󰂪")
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
