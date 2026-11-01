"""Portable cell frames and dependency-free still exporters."""

from __future__ import annotations
from html import escape
from itertools import groupby
from pathlib import Path

Color = tuple[int, int, int]
Cell = tuple[str, Color, Color]


def validate(frame):
    """Validate rectangular printable ASCII and 8-bit RGB, returning frozen rows."""
    rows = tuple(tuple(row) for row in frame)
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Frame must be a non-empty rectangular cell grid")
    for row in rows:
        for char, fg, bg in row:
            if len(char) != 1 or not " " <= char <= "~":
                raise ValueError("Cells require exactly one printable ASCII character")
            for color in (fg, bg):
                if len(color) != 3 or any(
                    not isinstance(v, int) or not 0 <= v <= 255 for v in color
                ):
                    raise ValueError("Colors require three integer channels in [0,255]")
    return rows


def from_text(text, fg=(120, 224, 208), bg=(10, 17, 28)):
    lines = text.splitlines() or [" "]
    width = max(1, max(map(len, lines)))
    return validate([[(ch, fg, bg) for ch in line.ljust(width)] for line in lines])


def to_text(frame):
    return "\n".join("".join(cell[0] for cell in row) for row in validate(frame))


def to_html(frame, title="GlyphForge Engine"):
    rows = validate(frame)
    lines = []
    for row in rows:
        parts = []
        for (fg, bg), cells in groupby(row, key=lambda cell: cell[1:]):
            text = escape("".join(cell[0] for cell in cells))
            parts.append(
                f'<span style="color:rgb{fg};background:rgb{bg}">{text}</span>'
            )
        lines.append("".join(parts))
    return (
        '<!doctype html><meta charset="utf-8"><title>' + escape(title) + "</title>"
        "<style>body{background:#0a111c;margin:32px;color:#cce7e1}"
        "pre{font:14px/1.2 monospace;white-space:pre;width:max-content}</style>"
        '<pre aria-label="'
        + escape(title, quote=True)
        + '">'
        + "\n".join(lines)
        + "</pre>"
    )


def to_svg(frame, title="GlyphForge Engine", cell_width=9, cell_height=18):
    rows = validate(frame)
    w, h = len(rows[0]) * cell_width, len(rows) * cell_height
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="#0a111c"/>',
    ]
    for y, row in enumerate(rows):
        for x, (char, fg, bg) in enumerate(row):
            xx, yy = x * cell_width, y * cell_height
            parts.append(
                f'<rect x="{xx}" y="{yy}" width="{cell_width}" height="{cell_height}" fill="rgb{bg}"/>'
            )
            if char != " ":
                parts.append(
                    f'<text x="{xx}" y="{yy + cell_height * 0.78}" fill="rgb{fg}" font-family="monospace" font-size="{cell_height * 0.82}" textLength="{cell_width}" lengthAdjust="spacingAndGlyphs">{escape(char)}</text>'
                )
    return "".join(parts) + "</svg>"


def save_frame(frame, path):
    """Write .html, .svg, .txt or .ans based on the filename extension."""
    from .ansi import encode

    path = Path(path)
    rows = validate(frame)
    exporters = {".html": to_html, ".svg": to_svg, ".txt": to_text, ".ans": encode}
    if path.suffix.lower() not in exporters:
        raise ValueError("Expected .html, .svg, .txt or .ans")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(exporters[path.suffix.lower()](rows), encoding="utf-8")
    return path
