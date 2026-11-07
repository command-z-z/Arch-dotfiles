#!/usr/bin/env python3
"""Read-only Codex CLI activity source for Linux; JSONL output, no hook setup.

Only logs held open by live Codex processes are inspected. Rollout files are an
internal format, so unknown records are ignored and missing values stay unknown.
Conversation text, reasoning text and command arguments are never emitted.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime
import json
import math
import os
from pathlib import Path
import time

MAX_READ = 2 * 1024 * 1024
COLORS = {"running": "#a6d189", "done": "#8caaee", "interrupted": "#e5c890",
          "unknown": "#a5adce", "offline": "#838ba7"}
LABELS = {"running": "进行中", "done": "已完成", "interrupted": "已中断",
          "unknown": "等待活动", "offline": "未运行"}


def number(value, default=0):
    try:
        n = float(value)
        return n if math.isfinite(n) and n >= 0 else default
    except (ValueError, TypeError):
        return default


def timestamp(value):
    if isinstance(value, (float, int)):
        return number(value)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError, OverflowError):
        return 0


def clean(value, limit=36):
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def duration(seconds):
    if seconds is None:
        return "—"
    seconds = int(max(0, seconds))
    if seconds >= 3600:
        return f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"
    return f"{seconds // 60:02}:{seconds % 60:02}"


@dataclass
class Session:
    id: str = ""
    parent: str = ""
    project: str = ""
    model: str = ""
    state: str = "unknown"
    activity: str = "等待会话事件"
    turn_id: str = ""
    started: float = 0
    ended: float = 0
    elapsed: float | None = None
    updated: float = 0
    context_used: float | None = None
    context_size: float = 0
    tools: int = 0

    def feed(self, record):
        if not isinstance(record, dict) or not isinstance(record.get("payload"), dict):
            return
        kind, p = record.get("type"), record["payload"]
        at = timestamp(record.get("timestamp"))
        if kind == "session_meta":
            # Forks can embed the parent's original metadata after their own header.
            if self.id:
                return
            self.id = str(p.get("id") or self.id)
            self.project = str(p.get("cwd") or self.project)
            source = p.get("source")
            self.parent = str(p.get("parent_thread_id") or "")
            if isinstance(source, dict) and source.get("subagent"):
                self.parent = self.parent or "subagent"
            return
        if kind == "turn_context":
            self.model = str(p.get("model") or self.model)
            return
        if kind == "event_msg":
            event = p.get("type")
            if event == "task_started":
                self.state, self.activity = "running", "正在处理任务"
                self.turn_id = str(p.get("turn_id") or "")
                self.started = timestamp(p.get("started_at")) or at
                self.ended, self.elapsed, self.tools = 0, None, 0
                self.context_size = number(p.get("model_context_window"), self.context_size)
            elif event in ("task_complete", "turn_aborted"):
                if p.get("turn_id") and self.turn_id and p["turn_id"] != self.turn_id:
                    return
                self.state = "done" if event == "task_complete" else "interrupted"
                self.activity = "本轮已完成，等待下一条指令" if self.state == "done" else "本轮已停止"
                self.ended = timestamp(p.get("completed_at")) or at
                self.elapsed = (number(p["duration_ms"]) / 1000 if "duration_ms" in p else
                                max(0, self.ended - self.started) if self.started else None)
            elif event == "token_count":
                info = p.get("info")
                if isinstance(info, dict):
                    usage = info.get("last_token_usage")
                    if isinstance(usage, dict):
                        self.context_used = number(usage.get("total_tokens"), None)
                    self.context_size = number(info.get("model_context_window"), self.context_size)
                # Usage events can arrive after task_complete; never reopen the turn.
                return
            elif event == "item_completed" and self.state == "running":
                item = p.get("item")
                if isinstance(item, dict):
                    labels = {"CommandExecution": "最近：命令执行完成", "FileChange": "最近：文件修改完成",
                              "McpToolCall": "最近：工具调用完成", "WebSearch": "最近：检索完成",
                              "SubAgentActivity": "最近：子代理协作", "AgentMessage": "最近：输出回复"}
                    self.activity = labels.get(item.get("type"), self.activity)
            else:
                return
        elif kind == "response_item" and self.state == "running":
            item_type = p.get("type")
            if item_type in ("function_call", "custom_tool_call"):
                self.tools += 1
                name = str(p.get("name") or "")
                if "apply_patch" in name:
                    self.activity = "最近：修改文件"
                elif "exec" in name or "shell" in name:
                    self.activity = "最近：执行工具"
                elif "search" in name or "web" in name:
                    self.activity = "最近：检索资料"
                else:
                    self.activity = "最近：调用工具"
            elif item_type == "message" and p.get("role") == "assistant":
                self.activity = "最近：输出回复"
            else:
                return
        else:
            return
        self.updated = max(self.updated, at, self.started, self.ended)


class Tail:
    def __init__(self, path):
        self.path = Path(path)
        self.session = Session()
        self.offset = 0
        self.identity = None
        self.pending = b""

    def update(self):
        with self.path.open("rb") as f:
            stat = os.fstat(f.fileno())
            identity = (stat.st_dev, stat.st_ino)
            if identity != self.identity or stat.st_size < self.offset:
                self.session, self.offset, self.pending = Session(), 0, b""
                self.identity = identity
            if self.offset == 0 and stat.st_size > MAX_READ:
                # Keep root/subagent metadata, then bound startup work on large histories.
                self._line(f.readline(MAX_READ))
                f.seek(stat.st_size - MAX_READ)
                f.readline(MAX_READ)  # discard a partial record at the seek boundary
                self.offset = f.tell()
            f.seek(self.offset)
            block = f.read(MAX_READ)
            self.offset = f.tell()
        data = self.pending + block
        lines = data.split(b"\n")
        self.pending = lines.pop()
        for line in lines:
            self._line(line)
        if len(self.pending) > MAX_READ:
            self.pending = b""  # an oversized unknown record must not grow memory forever

    def _line(self, line):
        try:
            self.session.feed(json.loads(line))
        except (ValueError, TypeError, UnicodeError, RecursionError):
            pass


def discover(codex_home, proc_root=Path("/proc")):
    count, paths = 0, set()
    sessions = (Path(codex_home) / "sessions").resolve()
    for proc in Path(proc_root).iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if (proc / "comm").read_text().strip() != "codex":
                continue
            count += 1
            for fd in (proc / "fd").iterdir():
                try:
                    path = fd.readlink()
                    if (path.name.startswith("rollout-") and path.suffix == ".jsonl"
                            and path.is_relative_to(sessions)):
                        paths.add(path)
                except OSError:
                    continue
        except OSError:
            continue
    return count, paths


def snapshot(sessions, process_count, now):
    roots = [s for s in sessions if not s.parent and s.id]
    selected = max(roots, key=lambda s: (s.state == "running", s.started, s.updated), default=None)
    state = selected.state if selected else "unknown" if process_count else "offline"
    color = COLORS[state]
    out = {"status": LABELS[state], "status_style": f"color: {color};",
           "project": "没有运行中的 Codex", "model": "CODEX CLI", "activity": "启动 Codex 后自动连接",
           "elapsed": "—", "tools": "—", "context_visible": False,
           "context_percent": 0, "context_label": "上下文数据尚未提供", "session_id": "",
           "agents": "主会话", "updated": "离线", "sessions": "0 个会话"}
    if not selected:
        if process_count:
            out.update(status="等待会话", project="Codex 已启动", activity="等待可读取的会话事件", updated="连接中")
        return out
    s = selected
    age = max(0, now - s.updated) if s.updated else None
    out.update(project=clean(Path(s.project).name or s.project or "未命名项目", 26),
               model=clean(s.model or "CODEX CLI", 32), activity=s.activity,
               elapsed=duration(now - s.started if state == "running" and s.started else s.elapsed),
               tools=str(s.tools) if s.started else "—", session_id=s.id, sessions=f"{len(roots)} 个会话",
               updated="刚刚更新" if age is not None and age < 5 else
                       f"{int(age)} 秒前" if age is not None and age < 60 else
                       f"{int(age // 60)} 分钟前" if age is not None else "等待更新")
    children = sum(1 for child in sessions if child.parent == s.id and child.state == "running")
    out["agents"] = f"{children} 个子代理运行中" if children else "主会话"
    if state == "running" and age is not None and age > 120:
        out.update(status="等待更新", status_style=f"color: {COLORS['unknown']};")
    if s.context_used is not None and s.context_size > 0:
        pct = min(100, max(0, 100 * s.context_used / s.context_size))
        out.update(context_visible=True, context_percent=round(pct, 1),
                   context_label=f"上下文  {pct:.0f}% · {s.context_used / 1000:.1f}k / {s.context_size / 1000:.0f}k")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", action="store_true", help="emit an update each second")
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    args = parser.parse_args()
    readers = {}
    while True:
        count, paths = discover(args.codex_home)
        readers = {path: readers.get(path) or Tail(path) for path in paths}
        current = []
        for reader in readers.values():
            try:
                reader.update()
                current.append(reader.session)
            except OSError:
                continue
        print(json.dumps(snapshot(current, count, time.time()), ensure_ascii=False), flush=True)
        if not args.listen:
            return
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
