"""Deterministic procedural cell shaders; no image assets or extra dependencies."""

import math
from glyphforge.frame import validate

RAMP = " .,:;irsXA253hMHGS#9B&@"


def rgb(a, b, t):
    t = max(0, min(1, t))
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def canvas(width, height, seconds, shader):
    rows = []
    for row in range(height):
        line = []
        for col in range(width):
            x = (col + 0.5 - width / 2) / max(height, 1) * 0.5
            y = (row + 0.5 - height / 2) / max(height, 1)
            value, fg, bg = shader(x, y, col, row, seconds)
            char = RAMP[max(0, min(len(RAMP) - 1, int(value * (len(RAMP) - 1))))]
            line.append((char, fg, bg))
        rows.append(line)
    return validate(rows)


def aurora(w, h, t):
    def shade(x, y, c, r, t):
        curtain = math.exp(-(((y + 0.12 - 0.08 * math.sin(x * 7 + t)) / 0.14) ** 2))
        curtain *= (0.5 + 0.5 * math.sin(x * 35 + math.sin(x * 8 + t) * 3)) ** 2
        stars = 1 if (c * 7919 + r * 104729) % 211 == 0 and y < 0.12 else 0
        v = max(stars, curtain)
        return (
            v,
            rgb((38, 180, 160), (180, 100, 245), 0.5 + 0.5 * math.sin(x * 4 + t)),
            rgb((3, 7, 21), (12, 65, 60), curtain * 0.8),
        )

    return canvas(w, h, t, shade)


def wormhole(w, h, t):
    def shade(x, y, c, r, t):
        radius = max(0.018, math.hypot(x, y))
        angle = math.atan2(y, x)
        bands = 0.5 + 0.5 * math.sin(2 / radius - t * 4 + angle * 3)
        v = bands * min(1, radius * 6)
        return (
            v,
            rgb((55, 220, 240), (245, 95, 195), 0.5 + 0.5 * math.sin(angle + t)),
            rgb((3, 4, 17), (45, 15, 65), v * 0.8),
        )

    return canvas(w, h, t, shade)


def ocean(w, h, t):
    def shade(x, y, c, r, t):
        if y < -0.07:
            sun = math.exp(-((x - 0.3) ** 2 + (y + 0.22) ** 2) * 280)
            return (
                sun,
                rgb((220, 131, 118), (255, 225, 154), sun),
                rgb((36, 23, 66), (205, 95, 91), (y + 0.5) * 1.8),
            )
        depth = y + 0.1
        wave = 0.5 + 0.5 * math.sin(
            x * 35 / (depth + 0.13) + t * 2 + math.sin(depth * 50 - t * 3)
        )
        reflection = math.exp(-(((x - 0.3) / (depth * 0.5 + 0.025)) ** 2)) * wave
        return (
            0.15 + wave * 0.5 + reflection * 0.3,
            rgb((51, 140, 173), (255, 206, 135), reflection),
            rgb((7, 24, 50), (35, 78, 111), wave * 0.5),
        )

    return canvas(w, h, t, shade)


def mandelbrot(w, h, t):
    def shade(x, y, c, r, t):
        zoom = 1.3 + 0.15 * math.sin(t * 0.4)
        point = complex(x * 3 / zoom - 0.65, y * 3 / zoom)
        z = 0j
        for n in range(45):
            z = z * z + point
            if abs(z) > 4:
                break
        else:
            return 0, (0, 0, 0), (3, 5, 12)
        v = (n / 45) ** 0.45
        return (
            0.2 + v * 0.8,
            rgb((45, 170, 220), (255, 180, 100), v),
            rgb((7, 17, 37), (90, 34, 95), v),
        )

    return canvas(w, h, t, shade)


def radar(w, h, t):
    def shade(x, y, c, r, t):
        radius = math.hypot(x, y)
        angle = math.atan2(y, x)
        sweep = (t - angle) % (2 * math.pi)
        glow = math.exp(-sweep * 2.3) if radius < 0.44 else 0
        ring = abs(radius * 12 - round(radius * 12)) < 0.10 and radius < 0.46
        cross = (abs(x) < 0.007 or abs(y) < 0.012) and radius < 0.46
        blip = any(
            math.hypot(x - bx, y - by) < 0.018
            for bx, by in ((0.2, 0.12), (-0.16, -0.25), (0.08, -0.3))
        )
        v = max(glow * 0.8, 0.3 if ring or cross else 0, 0.95 if blip else 0)
        return (
            v,
            rgb((20, 85, 65), (135, 255, 155), v),
            rgb((2, 12, 13), (8, 60, 32), glow),
        )

    return canvas(w, h, t, shade)


def lava(w, h, t):
    def shade(x, y, c, r, t):
        field = 0
        for i in range(6):
            bx = 0.35 * math.sin(t * 0.6 + i * 2.4)
            by = 0.32 * math.cos(t * 0.8 + i * 1.7)
            field += 0.008 / ((x - bx) ** 2 + (y - by) ** 2 + 0.003)
        v = max(0, min(1, (field - 0.25) * 1.2))
        return (
            v,
            rgb((196, 40, 90), (255, 224, 124), v),
            rgb((14, 5, 26), (150, 24, 70), v * 0.7),
        )

    return canvas(w, h, t, shade)


def interference(w, h, t):
    def shade(x, y, c, r, t):
        a = math.hypot(x - 0.23, y) * 42
        b = math.hypot(x + 0.23, y) * 42
        wave = (math.sin(a - t * 3) + math.sin(b - t * 3)) / 2
        v = abs(wave)
        return (
            v,
            rgb((61, 197, 237), (251, 129, 170), 0.5 + wave * 0.5),
            rgb((6, 13, 30), (46, 26, 76), v * 0.6),
        )

    return canvas(w, h, t, shade)


def starflight(w, h, t):
    rows = [[(" ", (180, 220, 255), (3, 5, 16)) for _ in range(w)] for _ in range(h)]
    for i in range(260):
        angle = i * 2.399963
        radius = ((((i * 1103515245 + 12345) & 65535) / 65536 + t * 0.18) % 1) ** 2
        x = round(w / 2 + math.cos(angle) * radius * w * 0.75)
        y = round(h / 2 + math.sin(angle) * radius * h * 0.75)
        if 0 <= x < w and 0 <= y < h:
            char = "." if radius < 0.3 else "+" if radius < 0.65 else "*"
            rows[y][x] = (char, rgb((47, 80, 137), (220, 245, 255), radius), (3, 5, 16))
    return rows
