"""Full-frame and changed-span ANSI encoding."""

from __future__ import annotations
import functools
import itertools
from dataclasses import dataclass


@functools.lru_cache(maxsize=8192)
def color256(rgb):
    levels = (0, 95, 135, 175, 215, 255)
    cube = tuple(min(range(6), key=lambda i: abs(levels[i] - v)) for v in rgb)
    cube_error = sum((levels[i] - v) ** 2 for i, v in zip(cube, rgb))
    grey = max(0, min(23, round((sum(rgb) / 3 - 8) / 10)))
    grey_error = sum((8 + 10 * grey - v) ** 2 for v in rgb)
    return (
        232 + grey
        if grey_error < cube_error
        else 16 + 36 * cube[0] + 6 * cube[1] + cube[2]
    )


def encode(buf, truecolor=True, x=1, y=1):
    parts = ["\x1b[0m"]
    last_fg = last_bg = None
    for r, row in enumerate(buf):
        parts.append(f"\x1b[{y + r};{x}H")
        for (ch, fg, bg), run in itertools.groupby(row):
            count = sum(1 for _ in run)
            params = []
            f = fg if truecolor else color256(fg)
            b = bg if truecolor else color256(bg)
            if ch != " " and f != last_fg:
                params.append(
                    f"38;2;{f[0]};{f[1]};{f[2]}" if truecolor else f"38;5;{f}"
                )
                last_fg = f
            if b != last_bg:
                params.append(
                    f"48;2;{b[0]};{b[1]};{b[2]}" if truecolor else f"48;5;{b}"
                )
                last_bg = b
            if params:
                parts.append("\x1b[" + ";".join(params) + "m")
            parts.append((ch or " ") * count)
    parts.append("\x1b[0m")
    return "".join(parts)


def dirty_rows(previous, current):
    """Return row indices whose terminal cells changed.

    Rows with a different width are considered dirty in full.  The function
    is intentionally pure so it can be used by tests and by a future renderer
    without coupling it to terminal state.
    """
    old_rows = tuple(tuple(row) for row in previous)
    new_rows = tuple(tuple(row) for row in current)
    if len(old_rows) != len(new_rows):
        return list(range(len(new_rows)))
    return [r for r, (old, new) in enumerate(zip(old_rows, new_rows)) if old != new]


def dirty_spans(previous, current):
    """Return changed half-open spans as ``(row, start, end)``.

    A shape change cannot be safely patched in place, so callers should use
    ``FrameSnapshot.needs_full`` for that case.  For equal-shaped frames this
    returns the smallest contiguous runs of changed cells.
    """
    old_rows = tuple(tuple(row) for row in previous)
    new_rows = tuple(tuple(row) for row in current)
    if len(old_rows) != len(new_rows) or any(
        len(a) != len(b) for a, b in zip(old_rows, new_rows)
    ):
        return [(r, 0, len(row)) for r, row in enumerate(new_rows)]
    spans = []
    for r, (old, new) in enumerate(zip(old_rows, new_rows)):
        start = None
        for c, (before, after) in enumerate(zip(old, new)):
            if before != after and start is None:
                start = c
            elif before == after and start is not None:
                spans.append((r, start, c))
                start = None
        if start is not None:
            spans.append((r, start, len(new)))
    return spans


def _encode_cells(cells, truecolor=True, x=1, y=1):
    """Encode independent cell runs with a fresh SGR state."""
    parts = ["\x1b[0m", f"\x1b[{y};{x}H"]
    last_fg = last_bg = None
    for (ch, fg, bg), run in itertools.groupby(cells):
        count = sum(1 for _ in run)
        params = []
        f = fg if truecolor else color256(fg)
        b = bg if truecolor else color256(bg)
        if ch != " " and f != last_fg:
            params.append(f"38;2;{f[0]};{f[1]};{f[2]}" if truecolor else f"38;5;{f}")
            last_fg = f
        if b != last_bg:
            params.append(f"48;2;{b[0]};{b[1]};{b[2]}" if truecolor else f"48;5;{b}")
            last_bg = b
        if params:
            parts.append("\x1b[" + ";".join(params) + "m")
        parts.append((ch or " ") * count)
    parts.append("\x1b[0m")
    return "".join(parts)


def encode_delta(previous, current, truecolor=True, x=1, y=1):
    """Encode only changed spans between equal-shaped terminal frames.

    Every span has an absolute cursor position and its own SGR reset.  This
    keeps cursor and color state independent between spans. The previous
    frame must have been displayed successfully.  ``None`` or a shape mismatch returns the existing full-frame
    encoding as the correctness fallback.
    """
    old_rows = tuple(tuple(row) for row in previous) if previous is not None else None
    new_rows = tuple(tuple(row) for row in current)
    if (
        old_rows is None
        or len(old_rows) != len(new_rows)
        or any(len(a) != len(b) for a, b in zip(old_rows, new_rows))
    ):
        return encode(new_rows, truecolor, x, y)
    parts = []
    for r, start, end in dirty_spans(old_rows, new_rows):
        parts.append(_encode_cells(new_rows[r][start:end], truecolor, x + start, y + r))
    return "".join(parts)


@dataclass
class FrameSnapshot:
    """Experimental frame cache for opt-in delta output.

    ``encode`` keeps the previous frame only after producing output.  Calling
    ``invalidate`` forces the next call to use the full-frame oracle, which is
    required after resize, palette changes, or any external screen mutation.
    """

    previous: tuple | None = None
    force_full: bool = True
    config: tuple | None = None

    def invalidate(self):
        self.force_full = True

    @property
    def needs_full(self):
        return self.force_full or self.previous is None

    def encode(self, buf, truecolor=True, x=1, y=1):
        current = tuple(tuple(row) for row in buf)
        config = (bool(truecolor), x, y)
        shape_changed = self.previous is not None and (
            len(self.previous) != len(current)
            or any(len(a) != len(b) for a, b in zip(self.previous, current))
        )
        config_changed = self.config is not None and self.config != config
        full = (
            self.force_full or self.previous is None or shape_changed or config_changed
        )
        output = (
            encode(current, truecolor, x, y)
            if full
            else encode_delta(self.previous, current, truecolor, x, y)
        )
        self.previous = current
        self.config = config
        self.force_full = False
        return output
