"""Read Codex activity through the existing monitor; no hooks or state files."""
import importlib.util
import os
from pathlib import Path
import sys


_path = Path(__file__).resolve().parents[1] / "agent-monitor/src/codex_monitor.py"
_spec = importlib.util.spec_from_file_location("_widgex_codex_monitor", _path)
monitor = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = monitor
_spec.loader.exec_module(monitor)


class Tracker:
    def __init__(self):
        self.home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
        self.readers = {}

    @staticmethod
    def select(sessions, process_count):
        roots = [s for s in sessions if not s.parent and s.id]
        selected = max(roots, key=lambda s: (s.state == "running", s.started, s.updated), default=None)
        if selected is None:
            return ("unknown" if process_count else "offline", "", "")
        return selected.state, selected.id, selected.turn_id

    def read(self):
        try:
            count, paths = monitor.discover(self.home)
        except OSError:
            return "unknown", "", ""
        self.readers = {path: self.readers.get(path) or monitor.Tail(path) for path in paths}
        sessions = []
        for reader in self.readers.values():
            try:
                reader.update()
                sessions.append(reader.session)
            except OSError:
                continue
        return self.select(sessions, count)


class Reaction:
    def __init__(self):
        self.current = ("unknown", "", "")
        self.wave_until = 0.0

    def accept(self, status, now):
        state, session, turn = status
        previous = self.current
        if (state == "done" and previous[0] == "running"
                and (session, turn) == previous[1:]):
            self.wave_until = now + 3.0
        elif state in {"running", "interrupted", "offline", "unknown"}:
            self.wave_until = 0.0
        self.current = status

    def mode(self, now):
        if self.current[0] == "running":
            return "running"
        if self.current[0] == "interrupted":
            return "waiting"
        if now < self.wave_until:
            return "wave"
        return "idle"
