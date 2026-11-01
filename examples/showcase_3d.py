"""Small authored 3D worlds: mesh geometry, depth and independent transforms."""

import math
from glyphforge import MeshEngine
from glyphforge.mesh import look_at, matrix
from .camera_scenes import add_box

FACES = "##++..@@%%::"


def box(engine, name, center, size, glyphs=FACES):
    return add_box(engine, name, center, size, glyphs)


def poly(engine, name, vertices, faces, glyphs="@#+:"):
    faces = list(faces)
    faces += [tuple(reversed(face)) for face in faces]
    return engine.add_mesh(
        name,
        vertices,
        faces,
        [glyphs[(i // 2) % len(glyphs)] for i in range(len(faces))],
    )


def jewel(engine, name, center, radius, glyphs="@#+:"):
    x, y, z = center
    vertices = [
        (x + radius, y, z),
        (x - radius, y, z),
        (x, y + radius, z),
        (x, y - radius, z),
        (x, y, z + radius),
        (x, y, z - radius),
    ]
    return poly(
        engine,
        name,
        vertices,
        [
            (0, 2, 4),
            (4, 2, 1),
            (1, 2, 5),
            (5, 2, 0),
            (0, 4, 3),
            (4, 1, 3),
            (1, 5, 3),
            (5, 0, 3),
        ],
        glyphs,
    )


def beam(engine, name, start, end, radius=0.06):
    direction = tuple(b - a for a, b in zip(start, end))
    length = math.sqrt(sum(v * v for v in direction))
    direction = tuple(v / length for v in direction)
    helper = (0, 1, 0) if abs(direction[1]) < 0.9 else (1, 0, 0)

    def cross(a, b):
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    right = cross(direction, helper)
    norm = math.sqrt(sum(v * v for v in right))
    right = tuple(v / norm for v in right)
    up = cross(direction, right)
    vertices = []
    for center in (start, end):
        for i in range(6):
            angle = math.tau * i / 6
            vertices.append(
                tuple(
                    center[j]
                    + radius * (right[j] * math.cos(angle) + up[j] * math.sin(angle))
                    for j in range(3)
                )
            )
    faces = []
    for i in range(6):
        j = (i + 1) % 6
        faces.extend(((i, j, j + 6), (i, j + 6, i + 6)))
    return poly(engine, name, vertices, faces, "+=")


def spacecraft(engine, t):
    vertices = [
        (0, 0, -2.4),
        (-0.5, -0.25, 0.9),
        (0.5, -0.25, 0.9),
        (0, 0.5, 0.4),
        (-2.3, -0.1, 1.2),
        (2.3, -0.1, 1.2),
        (-0.5, 0, 1.5),
        (0.5, 0, 1.5),
        (0, 1.1, 1.3),
    ]
    poly(
        engine,
        "ship",
        vertices,
        [
            (0, 1, 3),
            (0, 3, 2),
            (0, 2, 1),
            (1, 2, 3),
            (0, 4, 1),
            (0, 2, 5),
            (1, 6, 8),
            (2, 8, 7),
            (6, 7, 8),
        ],
        "@#+:.",
    )
    for x in (-0.45, 0.45):
        jewel(engine, f"engine-{x}", (x, -0.1, 1.6), 0.18, "@@")
    return (0, 0, 0), 7.2, (143, 213, 255)


def castle(engine, t):
    box(engine, "foundation", (0, -1.1, 0), (4.8, 0.2, 4.8), "............")
    for i, (x, z) in enumerate(((-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8))):
        box(engine, f"tower-{i}", (x, 0.1, z), (0.9, 2.4, 0.9))
        for j, (dx, dz) in enumerate(
            ((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3))
        ):
            box(engine, f"teeth-{i}-{j}", (x + dx, 1.5, z + dz), (0.25, 0.4, 0.25))
    for x in (-1.8, 1.8):
        box(engine, f"side-{x}", (x, -0.3, 0), (0.25, 1.4, 3.6))
    box(engine, "back", (0, -0.3, 1.8), (3.6, 1.4, 0.25))
    for x in (-1.2, 1.2):
        box(engine, f"gate-{x}", (x, -0.3, -1.8), (1.1, 1.4, 0.25))
    box(engine, "gate-lintel", (0, 0.3, -1.8), (1.5, 0.3, 0.25))
    return (0, 0, 0), 9, (222, 194, 145)


def bridge(engine, t):
    box(engine, "deck", (0, -0.4, 0), (6, 0.18, 1.4), "::++..==**##")
    for x in (-1.8, 1.8):
        for z in (-0.72, 0.72):
            box(engine, f"pier-{x}-{z}", (x, 0.45, z), (0.2, 2.5, 0.2))
        box(engine, f"crossbar-{x}", (x, 1.65, 0), (0.22, 0.18, 1.65))
    for z in (-0.7, 0.7):
        points = [(-3, 0, z), (-1.8, 1.6, z), (0, 0.4, z), (1.8, 1.6, z), (3, 0, z)]
        for i in range(4):
            beam(engine, f"cable-{z}-{i}", points[i], points[i + 1], 0.08)
        for i in range(9):
            x = -1.6 + i * 0.4
            top = 0.4 + abs(x) / 1.8 * 1.2
            beam(engine, f"hanger-{z}-{i}", (x, -0.3, z), (x, top, z), 0.055)
    return (0, 0.2, 0), 9, (132, 220, 213)


def orrery(engine, t):
    jewel(engine, "sun", (0, 0, 0), 0.7, "@#")
    for i, radius in enumerate((1.4, 2.15, 2.9)):
        angle = t * (0.8 - i * 0.18) + i * 1.6
        center = (
            radius * math.cos(angle),
            0.15 * math.sin(angle * 2),
            radius * math.sin(angle),
        )
        jewel(engine, f"planet-{i}", center, 0.22 + i * 0.06, "+@#")
        for j in range(20):
            a = math.tau * j / 20
            b = math.tau * (j + 1) / 20
            beam(
                engine,
                f"orbit-{i}-{j}",
                (radius * math.cos(a), 0, radius * math.sin(a)),
                (radius * math.cos(b), 0, radius * math.sin(b)),
                0.065,
            )
    return (0, 0, 0), 9, (255, 199, 113)


def staircase(engine, t):
    box(engine, "column", (0, 0, 0), (0.2, 3.7, 0.2))
    for i in range(16):
        angle = i * 0.42
        step = box(engine, f"step-{i}", (0, 0, 0), (1.25, 0.12, 0.42))
        step.set_transformation(
            matrix.compose(
                matrix.translation_h(
                    (0.72 * math.cos(angle), -1.6 + i * 0.2, 0.72 * math.sin(angle))
                ),
                matrix.rotation_h(-angle, (0, 1, 0)),
            )
        )
        x, z = 1.4 * math.cos(angle), 1.4 * math.sin(angle)
        beam(engine, f"rail-{i}", (x, -1.6 + i * 0.2, z), (x, -1 + i * 0.2, z), 0.055)
    return (0, 0, 0), 7.5, (187, 168, 248)


def molecule(engine, t):
    # A stylized tetrahedral structure, not a molecular simulation.
    center = (0, 0, 0)
    jewel(engine, "center", center, 0.52, "@#")
    for i, point in enumerate(
        ((1.2, 1.2, 1.2), (-1.2, -1.2, 1.2), (-1.2, 1.2, -1.2), (1.2, -1.2, -1.2))
    ):
        beam(engine, f"bond-{i}", center, point, 0.09)
        jewel(engine, f"atom-{i}", point, 0.38, "+*")
    return center, 7.5, (144, 236, 185)


def crystal(engine, t):
    for i in range(7):
        angle = i * 2.4
        radius = 0 if i == 0 else 1.1
        x, z = radius * math.cos(angle), radius * math.sin(angle)
        height = 2.7 if i == 0 else 1.1 + (i % 3) * 0.35
        vertices = [
            (
                x + 0.38 * math.cos(j * math.tau / 6),
                -1,
                z + 0.38 * math.sin(j * math.tau / 6),
            )
            for j in range(6)
        ]
        vertices += [
            (
                x + 0.38 * math.cos(j * math.tau / 6),
                height - 1.5,
                z + 0.38 * math.sin(j * math.tau / 6),
            )
            for j in range(6)
        ]
        vertices += [(x, height - 0.7, z)]
        faces = []
        for j in range(6):
            k = (j + 1) % 6
            faces.extend(((j, k, k + 6), (j, k + 6, j + 6), (j + 6, k + 6, 12)))
        poly(engine, f"crystal-{i}", vertices, faces, "@#+:")
    return (0, 0.1, 0), 7.3, (143, 211, 250)


def kinetic(engine, t):
    for i in range(9):
        size = 2.6 - i * 0.22
        angle = t * 0.5 + i * 0.24
        block = box(engine, f"layer-{i}", (0, 0, 0), (size, 0.16, size))
        block.set_transformation(
            matrix.compose(
                matrix.translation_h((0, -1 + i * 0.25, 0)),
                matrix.rotation_h(angle, (0, 1, 0)),
            )
        )
    return (0, 0, 0), 7, (247, 166, 166)


BUILDERS = {
    "spacecraft": spacecraft,
    "castle": castle,
    "bridge": bridge,
    "orrery": orrery,
    "staircase": staircase,
    "molecule": molecule,
    "crystal": crystal,
    "kinetic": kinetic,
}


def render(width, height, seconds, kind):
    with MeshEngine() as engine:
        target, radius, color = BUILDERS[kind](engine, seconds)
        angle = 0.45 + seconds * 0.35
        eye = (radius * math.sin(angle), radius * 0.45, -radius * math.cos(angle))
        camera = engine.create_camera(
            (width, height), ratio=width * 0.5 / height, fov=math.radians(48)
        )
        camera.set_transformation(look_at(eye, target))
        return engine.render_cells(camera, fg=color)
