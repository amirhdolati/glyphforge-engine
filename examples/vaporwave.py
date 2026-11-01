"""A camera-driven vaporwave landscape with a 3D neon grid and wireframe peaks."""

from __future__ import annotations

import math

from glyphforge.mesh import look_at, matrix

SKY_TOP = (9, 8, 32)
SKY_BOTTOM = (57, 17, 83)
SUN_STOPS = (
    (255, 230, 145),
    (255, 185, 135),
    (255, 111, 181),
    (212, 61, 226),
)
PINK = (255, 40, 221)
CYAN = (43, 200, 255)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def project(point, view, width, height, fov):
    """Project world coordinates into terminal cells, including cell aspect."""
    camera = matrix.transform_h(view, (*point, 1.0))
    depth = camera[2]
    if depth <= 0.08:
        return None
    ratio = width * 0.5 / height
    cot = 1.0 / math.tan(fov * 0.5)
    return (
        width * 0.5 + camera[0] * cot * width / (2 * ratio * depth),
        height * 0.5 - camera[1] * cot * height / (2 * depth),
        depth,
    )


def plot(buf, x, y, char, fg, bg=None):
    rows, cols = len(buf), len(buf[0])
    x, y = round(x), round(y)
    if 0 <= x < cols and 0 <= y < rows:
        old = buf[y][x]
        buf[y][x] = (char, fg, old[2] if bg is None else bg)


def segment(buf, a, b, color, char=None):
    if a is None or b is None:
        return
    x0, y0 = a[:2]
    x1, y1 = b[:2]
    length = max(1, round(max(abs(x1 - x0), abs(y1 - y0)) * 1.8))
    for step in range(length + 1):
        t = step / length
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        glyph = char or (
            "|"
            if abs(y1 - y0) > abs(x1 - x0) * 1.5
            else "/"
            if (x1 - x0) * (y1 - y0) < 0
            else "\\"
        )
        plot(buf, x, y, glyph, color)


def fill_polygon(buf, points, color, seed=0):
    points = [point for point in points if point is not None]
    if len(points) < 3:
        return
    ymin = max(0, math.floor(min(point[1] for point in points)))
    ymax = min(len(buf) - 1, math.ceil(max(point[1] for point in points)))
    for y in range(ymin, ymax + 1):
        crossings = []
        for a, b in zip(points, points[1:] + points[:1]):
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                crossings.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        crossings.sort()
        for left, right in zip(crossings[::2], crossings[1::2]):
            start, end = max(0, math.floor(left)), min(len(buf[0]), math.ceil(right))
            for x in range(start, end):
                depth = (y - ymin) / max(1, ymax - ymin)
                shade = 0.22 + depth * 0.32
                bg = mix(color, (7, 7, 27), shade)
                fleck = (x * 17 + y * 31 + seed) % 67 == 0
                plot(
                    buf, x, y, "." if fleck else " ", mix(bg, (100, 102, 191), 0.5), bg
                )


def mountain(center_z, width, seed, phase, scale, offset_x=0.0, count=39):
    """Generate two ridgeline rows with a craggy, triangulated profile."""
    rows = []
    for row, z in enumerate((center_z, center_z + 4.0)):
        vertices = []
        for i in range(count):
            x = offset_x - width / 2 + width * i / (count - 1)
            envelope = max(0.0, 1.0 - abs(x) / (width * 0.56))
            crag = (
                0.36
                + abs(math.sin((i + seed) * 1.11)) * 0.82
                + abs(math.sin((i + seed) * 0.39 + 0.8)) * 0.7
            )
            y = -1.05 + envelope * crag * scale * (1.0 if row == 0 else 0.8)
            y += 0.08 * math.sin(phase + i * 0.31 + row * 0.9)
            vertices.append((x, y, z))
        rows.append(vertices)
    return rows


def draw_ridge(buf, view, width, height, fov, geometry, fill, wire, seed):
    front, back = geometry
    front2 = [project(point, view, width, height, fov) for point in front]
    back2 = [project(point, view, width, height, fov) for point in back]
    floor2 = [
        project((point[0], -1.06, point[2]), view, width, height, fov)
        for point in front
    ]
    fill_polygon(buf, front2 + floor2[::-1], fill, seed)
    for i in range(len(front) - 1):
        segment(buf, front2[i], front2[i + 1], wire, "/" if i % 2 else "\\")
        segment(buf, back2[i], back2[i + 1], mix(wire, (40, 50, 168), 0.45), "_")
        segment(buf, front2[i], back2[i + 1], wire, "/" if i % 2 else "\\")
        if i % 2 == 0:
            segment(buf, front2[i + 1], back2[i], mix(wire, (80, 70, 210), 0.24), "\\")
    for i in range(len(front)):
        segment(buf, front2[i], back2[i], wire, "|")
    for i in range(1, len(front) - 1):
        if front[i][1] > front[i - 1][1] and front[i][1] >= front[i + 1][1]:
            plot(buf, front2[i][0], front2[i][1], "^", mix(wire, (220, 220, 255), 0.35))


def draw_grid(buf, view, width, height, fov, near, far, foreground=False):
    ground = -1.06
    if foreground:
        distances = (-6.0, -4.0, -2.0, -0.4, 1.1, 2.4, 4.2, 6.2, 8.4)
        x_extent, spacing = 18, 1.0
        color_near, color_far = (255, 39, 223), (174, 38, 251)
    else:
        distances = (13, 20, 30)
        x_extent, spacing = 20, 1.35
        color_near, color_far = (210, 43, 241), (102, 44, 183)

    for index, x in enumerate(
        [
            i * spacing
            for i in range(-int(x_extent / spacing), int(x_extent / spacing) + 1)
        ]
    ):
        a = project((x, ground, -6.0 if foreground else near), view, width, height, fov)
        b = project((x, ground, far), view, width, height, fov)
        edge = abs(x) / x_extent
        color = mix(color_near, color_far, edge * 0.72)
        segment(buf, a, b, color, "|" if index == int(x_extent / spacing) else None)

    for index, z in enumerate(distances):
        a = project((-x_extent, ground, z), view, width, height, fov)
        b = project((x_extent, ground, z), view, width, height, fov)
        color = mix(color_near, color_far, index / max(1, len(distances) - 1) * 0.72)
        segment(buf, a, b, color, "=" if index % 2 == 0 else "-")


def frame(width, height, seconds):
    if width < 1 or height < 1:
        raise ValueError("Frame size must be positive")
    width, height = int(width), int(height)
    fov = math.radians(52)
    eye = (0.85 * math.sin(seconds * 0.654), 2.25, -8.0)
    target = (0.0, 1.9, 8.0)
    view = look_at(eye, target)

    # Layered twilight color, a soft neon haze, and a stable, twinkling starfield.
    buf = []
    for y in range(height):
        t = y / max(1, height - 1)
        row = []
        for x in range(width):
            base = mix(SKY_TOP, SKY_BOTTOM, t * 0.9)
            haze = math.exp(-(((t - 0.53) / 0.18) ** 2)) * (
                0.13 + 0.09 * math.sin(x * 0.12)
            )
            sky = mix(base, (135, 31, 139), haze)
            row.append((" ", sky, sky))
        buf.append(row)

    for i in range(max(34, width * height // 24)):
        x = (i * 7919 + 17) % width
        y = (i * 3571 + 5) % max(1, int(height * 0.55))
        twinkle = 0.48 + 0.52 * math.sin(seconds * 1.6 + i * 2.17)
        color = mix((92, 94, 173), (245, 218, 255), twinkle)
        plot(buf, x, y, "+" if i % 11 == 0 else ".", color)

    # Subtle distant grid and horizon glow sit behind both mountain ridges.
    draw_grid(buf, view, width, height, fov, 9.5, 58, foreground=False)

    horizon = project((0, -1.06, 58), view, width, height, fov)
    hy = round(horizon[1]) if horizon else height // 2
    for x in range(width):
        plot(buf, x, hy, "=" if x % 8 else "+", mix((115, 38, 172), PINK, 0.38))

    # A broad sunset disk, with warm gradients, a halo, and broken synth scanlines.
    center = project((0, 4.2, 14.2), view, width, height, fov)
    if center:
        sx, sy, depth = center
        radius_y = max(4.2, min(height * 0.22, width * 0.12) * 14 / depth)
        radius_x = radius_y * 1.85
        y0, y1 = (
            max(0, math.floor(sy - radius_y)),
            min(height, math.ceil(sy + radius_y)),
        )
        for y in range(y0, y1):
            dy = (y + 0.5 - sy) / radius_y
            if abs(dy) >= 1:
                continue
            half = radius_x * math.sqrt(1 - dy * dy)
            shade = (dy + 1) * 0.5 * (len(SUN_STOPS) - 1)
            band = min(len(SUN_STOPS) - 2, int(shade))
            sun = mix(SUN_STOPS[band], SUN_STOPS[band + 1], shade - band)
            for x in range(
                max(0, math.floor(sx - half)), min(width, math.ceil(sx + half))
            ):
                dx = (x + 0.5 - sx) / radius_x
                scanline = dy > 0.2 and dy < 0.9 and (y - round(sy)) % 2 == 0
                halo = max(0.0, 1.0 - math.hypot(dx, dy) / 1.8) * 0.32
                bg = mix(sun, (92, 31, 121), 0.48) if scanline else sun
                bg = mix(bg, (255, 225, 204), halo * 0.18)
                plot(buf, x, y, " ", sun, bg)

    # The far ridge fades into the glow; the nearer ridge carries the sharp lattice.
    far = mountain(17.0, 36.0, 23, 1.1, 2.0)
    middle = mountain(13.5, 28.0, 14, 2.0, 1.7, offset_x=5.0)
    near = mountain(9.5, 21.5, 41, 0.0, 2.35)
    draw_ridge(buf, view, width, height, fov, far, (19, 17, 59), (48, 91, 227), 23)
    draw_ridge(buf, view, width, height, fov, middle, (22, 19, 69), (123, 83, 237), 14)
    draw_ridge(buf, view, width, height, fov, near, (18, 24, 77), CYAN, 41)

    # The foreground half of the floor completes the perspective and depth cues.
    draw_grid(buf, view, width, height, fov, -6.0, 9.2, foreground=True)

    # A few perspective glints add a vanishing-point cue to the neon runway.
    for i in range(5):
        z = 2.1 + i * 1.05
        p = project((0, -1.055, z), view, width, height, fov)
        if p and 0 <= round(p[1]) < height:
            glow = mix((255, 63, 229), (122, 89, 255), i / 5)
            plot(buf, width // 2, p[1], "+", glow)
    return buf


if __name__ == "__main__":
    from .common import run

    run(frame, __doc__)
