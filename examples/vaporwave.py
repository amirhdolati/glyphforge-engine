"""A 3D vaporwave horizon: striped sunset, wireframe peaks and neon grid."""

import math
from glyphforge import MeshEngine
from glyphforge.mesh import look_at
from .showcase_3d import beam


PALETTE = {
    "grid": (255, 35, 224),
    "mountain": (39, 138, 255),
    "sun": (255, 157, 196),
    "sun_bright": (255, 218, 133),
    "star": (153, 142, 255),
    "sky": (19, 12, 48),
}


def build_sun(engine, center=(0, 2.2, 10), radius=1.55):
    """Make a sunset disk from thin 3D bars, leaving gaps between stripes."""
    cx, cy, cz = center
    rows = 18
    for i in range(rows):
        y0 = cy - radius + 2 * radius * i / rows
        y1 = cy - radius + 2 * radius * (i + 1) / rows - 0.035
        mid = (y0 + y1) / 2
        half = radius * math.sqrt(max(0, 1 - ((mid - cy) / radius) ** 2))
        z = cz - 0.035
        verts = (
            (cx - half, y0, z),
            (cx + half, y0, z),
            (cx + half, y1, z),
            (cx - half, y1, z),
        )
        glyph = "S" if mid > cy + 0.35 else "s"
        engine.add_mesh(
            f"sun-band-{i}",
            verts,
            ((0, 1, 2), (0, 2, 3), (2, 1, 0), (3, 2, 0)),
            (glyph,) * 4,
        )


def build_mountains(engine, seconds):
    """Triangular wireframe ridges with a gently moving silhouette."""
    xs = [-5.8 + i * 0.58 for i in range(21)]
    rows = []
    for depth in (3.5, 5.1):
        row = []
        for i, x in enumerate(xs):
            envelope = max(0, 1 - abs(x) / 6)
            ridge = (
                0.30
                + abs(math.sin(i * 1.7)) * 0.85
                + abs(math.sin(i * 0.61 + 1.2)) * 0.7
            )
            y = -0.08 + envelope * ridge + 0.08 * math.sin(seconds * 0.6 + i * 0.35)
            row.append((x, y, depth))
        rows.append(row)
    front, back = rows
    for i in range(len(xs) - 1):
        beam(engine, f"mountain-front-{i}", front[i], front[i + 1], 0.027)
        beam(engine, f"mountain-back-{i}", back[i], back[i + 1], 0.025)
        beam(engine, f"mountain-cross-{i}", front[i], back[i + 1], 0.021)
        if i % 2 == 0:
            beam(engine, f"mountain-cross2-{i}", front[i + 1], back[i], 0.018)
    for i in range(0, len(xs), 2):
        beam(engine, f"mountain-depth-{i}", front[i], back[i], 0.022)


def build_grid(engine):
    """Build an actual perspective floor grid from narrow triangle strips."""
    z_near, z_far = -0.2, 22
    for i in range(25):
        x = -8 + i * (16 / 24)
        verts = (
            (x - 0.045, -0.82, z_near),
            (x + 0.045, -0.82, z_near),
            (x + 0.045, -0.82, z_far),
            (x - 0.045, -0.82, z_far),
        )
        engine.add_mesh(
            f"grid-long-{i}",
            verts,
            ((0, 1, 2), (0, 2, 3), (2, 1, 0), (3, 2, 0)),
            ("G",) * 4,
        )
    for j in range(19):
        t = j / 18
        z = z_near + (z_far - z_near) * t
        half = 8 * (1 - t) + 0.4 * t
        thickness = 0.08 * (1 - t) + 0.025 * t
        verts = (
            (-half, -0.82, z - thickness),
            (half, -0.82, z - thickness),
            (half, -0.82, z + thickness),
            (-half, -0.82, z + thickness),
        )
        engine.add_mesh(
            f"grid-cross-{j}",
            verts,
            ((0, 1, 2), (0, 2, 3), (2, 1, 0), (3, 2, 0)),
            ("G",) * 4,
        )


def build_stars(engine):
    """Place sparse 3D stars behind the sun and ridges."""
    for i in range(90):
        x = (((i * 7919) % 997) / 997 - 0.5) * 15
        y = 0.3 + ((i * 3571) % 991) / 991 * 5.5
        z = 14 + ((i * 2017) % 983) / 983 * 5
        size = 0.018 if i % 5 else 0.032
        verts = (
            (x - size, y, z),
            (x + size, y, z),
            (x, y + size, z),
            (x, y - size, z),
            (x, y, z - size),
            (x, y, z + size),
        )
        faces = (
            (0, 2, 4),
            (4, 2, 1),
            (1, 2, 5),
            (5, 2, 0),
            (0, 4, 3),
            (4, 1, 3),
            (1, 5, 3),
            (5, 0, 3),
        )
        faces = faces + tuple(tuple(reversed(face)) for face in faces)
        engine.add_mesh(f"star-{i}", verts, faces, (".",) * len(faces))


def frame(width, height, seconds):
    with MeshEngine() as engine:
        build_stars(engine)
        build_sun(
            engine, center=(0, 2.05, 10), radius=1.58 + 0.035 * math.sin(seconds * 0.7)
        )
        build_mountains(engine, seconds)
        build_grid(engine)
        eye = (0.14 * math.sin(seconds * 0.32), 1.55, -8.2)
        target = (0, -0.15, 5.3)
        camera = engine.create_camera(
            (width, height), ratio=width * 0.5 / height, fov=math.radians(49)
        )
        camera.set_transformation(look_at(eye, target))
        raw = engine.render_frame(camera, as_str=True)
        palette = {
            "G": PALETTE["grid"],
            "/": PALETTE["mountain"],
            "\\": PALETTE["mountain"],
            "S": PALETTE["sun_bright"],
            "s": PALETTE["sun"],
            " .": PALETTE["star"],
            ".": PALETTE["star"],
        }
        rows = []
        for line in raw.splitlines():
            row = []
            for char in line:
                fg = palette.get(
                    char, (201, 85, 221) if char in ("+", "*", "#") else PALETTE["sky"]
                )
                bg = (19, 12, 48) if char == " " else (20, 12, 50)
                row.append((char, fg, bg))
            rows.append(row)
        # A crisp terminal-cell grid reinforces the projected 3D floor below
        # the triangle-rendered horizon. Its lines share the camera's vanishing point.
        horizon = max(1, min(height - 2, round(height * 0.52)))
        for y in range(horizon, height):
            depth = (y - horizon + 1) / (height - horizon)
            spread = max(1, round((width * 0.48) * depth))
            for band in range(-10, 11):
                x = round((width - 1) / 2 + band * spread / 10)
                if 0 <= x < width:
                    rows[y][x] = (
                        "|" if band == 0 else "/" if band < 0 else chr(92),
                        PALETTE["grid"],
                        (22, 8, 48),
                    )
        step = 1
        y = horizon + 1
        while y < height:
            for x in range(width):
                old = rows[y][x][0]
                rows[y][x] = (
                    "+" if old in ("|", "/", "\\") else "=",
                    PALETTE["grid"],
                    (29, 7, 56),
                )
            step = max(1, round(step * 1.34))
            y += step
        return rows


if __name__ == "__main__":
    from .common import run

    run(frame, __doc__)
