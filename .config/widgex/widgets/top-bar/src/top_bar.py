#!/usr/bin/env python3
"""JSON source for the Widgex top bar."""
import json
import os
import re
import shutil
import subprocess
import time


WORKSPACE_ICONS = {
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
}


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


def workspace_payload():
    active = active_workspace_name()
    payload = {}
    for n, icon in WORKSPACE_ICONS.items():
        payload[f"workspace{n}"] = icon
        payload[f"workspace{n}_style"] = (
            "background: var(--ctp-green); color: var(--ctp-mantle)" if n == active else ""
        )
    return payload


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
    return f" {paused}{text}"


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
        return f" {round((total - available) / total * 100)}%"
    except Exception:
        return " --%"


def disk_percent():
    try:
        usage = shutil.disk_usage("/")
        return f" {round(usage.used / usage.total * 100)}%"
    except Exception:
        return " --%"


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
                return " " + connection
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


def github_notifications():
    output = run(["gh", "api", "notifications"], timeout=1.2)
    try:
        count = len(json.loads(output))
        return f" {count}"
    except Exception:
        return " --"


def updates():
    output = run(["waybar-module-pacman-updates"], timeout=1.2)
    if not output:
        return ""
    try:
        data = json.loads(output)
        text = str(data.get("text") or "").strip()
        alt = str(data.get("alt") or "")
        icon = "" if "has-updates" in alt or text not in {"", "0"} else ""
        return f"{icon} {text}".strip()
    except Exception:
        return output.splitlines()[0][:16]


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


def clock():
    return time.strftime("%a %d, %b  %I:%M %p")


def main():
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
        "notifications": notifications(),
        "clock": clock(),
    }
    payload.update(workspace_payload())
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
