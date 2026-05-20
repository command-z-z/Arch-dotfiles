#!/usr/bin/env python3
"""Per-slot read / new / delete for the widgex memo widget."""
import json, os, shlex, shutil, subprocess, sys

NOTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notes")
SLOTS = tuple(range(1, 11))


def path(n):
    return os.path.join(NOTES_DIR, f"{n}.txt")


def content(n):
    p = path(n)
    if not os.path.isfile(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read().strip()


def read(n):
    text = content(n)
    print(json.dumps({"text": text, "display": "flex" if text else "none"}))


def read_all():
    out = {}
    for n in SLOTS:
        text = content(n)
        out[f"note{n}_text"] = text
        out[f"note{n}_display"] = "flex" if text else "none"
    print(json.dumps(out))


def open_editor(file_path):
    editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nvim")
    if shutil.which("kitty"):
        subprocess.Popen(["kitty", *editor, file_path])
    elif shutil.which("alacritty"):
        subprocess.Popen(["alacritty", "-e", *editor, file_path])
    else:
        subprocess.Popen(["xdg-open", file_path])


def new():
    os.makedirs(NOTES_DIR, exist_ok=True)
    for n in SLOTS:
        if not content(n):
            open(path(n), "a", encoding="utf-8").close()
            open_editor(path(n))
            return


def edit(n):
    os.makedirs(NOTES_DIR, exist_ok=True)
    open(path(n), "a", encoding="utf-8").close()
    open_editor(path(n))


def delete(n):
    p = path(n)
    if os.path.isfile(p):
        os.remove(p)


def main():
    a = sys.argv[1:]
    if not a:
        return
    if a[0] == "read":
        read(int(a[1]))
    elif a[0] == "read_all":
        read_all()
    elif a[0] == "new":
        new()
    elif a[0] == "edit":
        edit(int(a[1]))
    elif a[0] == "delete":
        delete(int(a[1]))


if __name__ == "__main__":
    main()
