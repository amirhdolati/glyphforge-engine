"""Incremental legacy/Kitty keyboard and mouse event parser."""

from __future__ import annotations
import re
import time
from dataclasses import dataclass


@dataclass
class Event:
    key: str = ""
    shift: bool = False
    release: bool = False
    repeat: bool = False
    enhanced: bool = False
    mouse: tuple | None = None


class Input:
    def __init__(self):
        self.pending = ""
        self.escape_at = 0.0

    def feed(self, data=b"", now=None):
        now = time.monotonic() if now is None else now
        self.pending += data.decode("ascii", "ignore")
        events = []
        while self.pending:
            s = self.pending
            if s[0] != "\x1b":
                self.pending = s[1:]
                ch = s[0]
                key = {
                    "\x03": "exit",
                    "\t": "tab",
                    "\n": "enter",
                    "\r": "enter",
                    " ": "space",
                    "\x7f": "backspace",
                }.get(ch, ch.lower())
                events.append(Event(key, shift=ch.isupper()))
                continue
            if s == "\x1b":
                if not self.escape_at:
                    self.escape_at = now
                if now - self.escape_at > 0.06:
                    self.pending = ""
                    self.escape_at = 0
                    events.append(Event("exit"))
                break
            self.escape_at = 0
            if s[1] not in "[O":
                self.pending = s[2:]
                continue
            if len(s) == 2:
                break
            if s[1] == "O":
                self.pending = s[3:]
                key = {
                    "A": "up",
                    "B": "down",
                    "C": "right",
                    "D": "left",
                    "H": "home",
                }.get(s[2])
                if key:
                    events.append(Event(key))
                continue
            match = re.match(r"\x1b\[([0-?]*)([ -/]*)([@-~])", s)
            if not match:
                if len(s) > 128:
                    self.pending = s[1:]
                else:
                    break
                continue
            self.pending = s[match.end() :]
            body, _, final = match.groups()
            try:
                if body.startswith("<") and final in "Mm":
                    button, mx, my = map(int, body[1:].split(";"))
                    if button & 32:
                        events.append(Event(mouse=(mx, my)))
                elif final == "u":
                    seg = body.split(";")
                    code = int(seg[0].split(":")[0])
                    mods = seg[1].split(":") if len(seg) > 1 else ["1"]
                    mask = int(mods[0] or "1") - 1
                    event = int(mods[1]) if len(mods) > 1 and mods[1] else 1
                    key = {
                        27: "exit",
                        9: "tab",
                        13: "enter",
                        32: "space",
                        57417: "left",
                        57418: "right",
                        57419: "up",
                        57420: "down",
                        57423: "home",
                        57441: "shift-left",
                        57447: "shift-right",
                    }.get(code)
                    if key is None and 32 <= code <= 126:
                        key = chr(code).lower()
                    if code == 99 and mask & 4:
                        key = "exit"
                    if key:
                        events.append(
                            Event(key, bool(mask & 1), event == 3, event == 2, True)
                        )
                elif final in "ABCDH":
                    key = {
                        "A": "up",
                        "B": "down",
                        "C": "right",
                        "D": "left",
                        "H": "home",
                    }[final]
                    modifiers = body.split(";")[-1].split(":") if ";" in body else ["1"]
                    mods = int(modifiers[0] or "1") - 1
                    kind = int(modifiers[1]) if len(modifiers) > 1 else 1
                    events.append(
                        Event(key, bool(mods & 1), kind == 3, kind == 2, ":" in body)
                    )
                elif final == "~" and body in ("1", "7"):
                    events.append(Event("home"))
                elif final == "O" and not body:
                    events.append(Event("focus-out"))
            except (ValueError, OverflowError):
                continue
        return events
