#!/usr/bin/env python3
"""
widgex notification daemon.
Registers org.freedesktop.Notifications on the session bus (replaces swaync).
Outputs full JSON state to stdout on every change (widgex listen-mode source).
Control commands are read from ~/.cache/widgex/notif-cmd (written by notif_ctrl.sh).
"""
import json
import os
import re
import subprocess
from collections import OrderedDict
from datetime import datetime

from gi.repository import GLib  # type: ignore[attr-defined]
from pydbus import SessionBus
from pydbus.generic import signal as dbus_signal

CACHE_DIR = os.path.expanduser("~/.cache/widgex")
CMD_FILE = os.path.join(CACHE_DIR, "notif-cmd")
DND_FILE = os.path.join(CACHE_DIR, "dnd")
MAX_SLOTS = 20

IFACE_XML = """
<node>
  <interface name="org.freedesktop.Notifications">
    <method name="GetCapabilities">
      <arg name="caps" type="as" direction="out"/>
    </method>
    <method name="Notify">
      <arg name="app_name"       type="s"     direction="in"/>
      <arg name="replaces_id"    type="u"     direction="in"/>
      <arg name="app_icon"       type="s"     direction="in"/>
      <arg name="summary"        type="s"     direction="in"/>
      <arg name="body"           type="s"     direction="in"/>
      <arg name="actions"        type="as"    direction="in"/>
      <arg name="hints"          type="a{sv}" direction="in"/>
      <arg name="expire_timeout" type="i"     direction="in"/>
      <arg name="id"             type="u"     direction="out"/>
    </method>
    <method name="CloseNotification">
      <arg name="id" type="u" direction="in"/>
    </method>
    <method name="GetServerInformation">
      <arg name="name"         type="s" direction="out"/>
      <arg name="vendor"       type="s" direction="out"/>
      <arg name="version"      type="s" direction="out"/>
      <arg name="spec_version" type="s" direction="out"/>
    </method>
    <signal name="NotificationClosed">
      <arg name="id"     type="u"/>
      <arg name="reason" type="u"/>
    </signal>
    <signal name="ActionInvoked">
      <arg name="id"         type="u"/>
      <arg name="action_key" type="s"/>
    </signal>
  </interface>
</node>
"""

ICON_BELL     = ""   #   nf-md-bell
ICON_BELL_OFF = ""   #   nf-md-bell-off


class NotifDaemon:
    dbus = IFACE_XML
    NotificationClosed = dbus_signal()  # type: ignore[assignment]
    ActionInvoked      = dbus_signal()  # type: ignore[assignment]

    def __init__(self):
        self._next_id: int = 1
        self._notifs: OrderedDict = OrderedDict()
        self._dnd: bool = self._load_dnd()
        self._volume: int = 0
        self._last_out: str | None = None
        os.makedirs(CACHE_DIR, exist_ok=True)

    # ── dbus interface ──────────────────────────────────────────────────────

    def GetCapabilities(self):
        return ["body", "actions", "persistence"]

    def GetServerInformation(self):
        return ("widgex-notif", "widgex", "1.0", "1.2")

    def Notify(self, app_name, replaces_id, _app_icon, summary, body,
               _actions, hints, _expire_timeout):
        nid = replaces_id if replaces_id else self._next_id
        if not replaces_id:
            self._next_id += 1

        urgency = 1
        try:
            if hints and "urgency" in hints:
                v = hints["urgency"]
                urgency = v.unpack() if hasattr(v, "unpack") else int(v)
        except Exception:
            pass

        self._notifs[nid] = {
            "app":    app_name or "Notification",
            "title":  summary or "",
            "body":   body or "",
            "time":   datetime.now().strftime("%H:%M"),
            "urgent": urgency >= 2,
        }
        while len(self._notifs) > MAX_SLOTS:
            del self._notifs[next(iter(self._notifs))]

        self._emit()
        return nid

    def CloseNotification(self, nid):
        if nid in self._notifs:
            del self._notifs[nid]
            self._emit()
        self.NotificationClosed(nid, 3)  # type: ignore[operator]

    # ── control commands ────────────────────────────────────────────────────

    def _check_cmd(self):
        if not os.path.exists(CMD_FILE):
            return True
        try:
            with open(CMD_FILE) as f:
                cmd = f.read().strip()
            os.unlink(CMD_FILE)
        except OSError:
            return True

        if cmd == "toggle-dnd":
            self._dnd = not self._dnd
            self._save_dnd()
            self._emit()
        elif cmd == "clear":
            ids = list(self._notifs.keys())
            self._notifs.clear()
            for nid in ids:
                self.NotificationClosed(nid, 3)  # type: ignore[operator]
            self._emit()
        elif cmd.startswith("close-"):
            try:
                slot = int(cmd[6:])
                keys = list(self._notifs.keys())
                if 1 <= slot <= len(keys):
                    nid = keys[slot - 1]
                    del self._notifs[nid]
                    self.NotificationClosed(nid, 2)  # type: ignore[operator]
                    self._emit()
            except (ValueError, IndexError):
                pass
        return True

    def _poll_volume(self):
        vol = self._get_volume()
        if vol != self._volume:
            self._volume = vol
            self._emit()
        return True

    # ── helpers ─────────────────────────────────────────────────────────────

    def _load_dnd(self) -> bool:
        try:
            with open(DND_FILE) as f:
                return f.read().strip() == "true"
        except OSError:
            return False

    def _save_dnd(self):
        with open(DND_FILE, "w") as f:
            f.write("true" if self._dnd else "false")

    def _get_volume(self) -> int:
        try:
            out = subprocess.check_output(
                ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                text=True, timeout=1, stderr=subprocess.DEVNULL,
            )
            m = re.search(r"(\d+)%", out)
            return int(m.group(1)) if m else 0
        except Exception:
            return 0

    def _emit(self):
        notifs = list(self._notifs.values())
        data: dict = {
            "dnd":        "true" if self._dnd else "false",
            "dnd_label":  ICON_BELL_OFF if self._dnd else ICON_BELL,
            "dnd_style":  "color: #8aadf4" if self._dnd else "",
            "volume_pct": str(self._volume),
        }
        for i in range(1, MAX_SLOTS + 1):
            if i <= len(notifs):
                n = notifs[i - 1]
                data.update({
                    f"notif_{i}_display":      "block",
                    f"notif_{i}_app":          n["app"],
                    f"notif_{i}_title":        n["title"],
                    f"notif_{i}_body":         n["body"],
                    f"notif_{i}_time":         n["time"],
                    f"notif_{i}_urgent_style": "background: #ed8796;" if n["urgent"] else "",
                })
            else:
                data.update({
                    f"notif_{i}_display":      "none",
                    f"notif_{i}_app":          "",
                    f"notif_{i}_title":        "",
                    f"notif_{i}_body":         "",
                    f"notif_{i}_time":         "",
                    f"notif_{i}_urgent_style": "",
                })

        line = json.dumps(data, ensure_ascii=False)
        if line != self._last_out:
            print(line, flush=True)
            self._last_out = line
            # Write compact status for top_bar.py
            status = {"count": len(notifs), "dnd": self._dnd}
            try:
                with open(os.path.join(CACHE_DIR, "notif-status.json"), "w") as f:
                    json.dump(status, f)
            except OSError:
                pass


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    bus = SessionBus()
    daemon = NotifDaemon()
    daemon._volume = daemon._get_volume()
    daemon._emit()

    pub = bus.publish("org.freedesktop.Notifications", daemon)  # noqa: F841

    loop = GLib.MainLoop()
    GLib.timeout_add(100, daemon._check_cmd)
    GLib.timeout_add(2000, daemon._poll_volume)
    loop.run()


if __name__ == "__main__":
    main()
