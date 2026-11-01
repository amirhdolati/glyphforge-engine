"""Static triangle geometry for demos that animate only the camera."""

import math
from glyphforge import MeshEngine
from glyphforge.mesh import look_at
from .rotating_cube import TRIANGLES, VERTICES


def add_box(engine, name, center, size, glyphs):
    vertices = [
        tuple(center[i] + v[i] * size[i] / 2 for i in range(3)) for v in VERTICES
    ]
    return engine.add_mesh(name, vertices, TRIANGLES, glyphs)


def render(width, height, seconds, mode):
    with MeshEngine() as engine:
        if mode == "orbit":
            # A recognisable robot sculpture, authored once in world coordinates.
            pieces = [
                ("base", (0, -1.45, 0), (3, 0.25, 2), "::++..==**##"),
                ("body", (0, 0.1, 0), (1.2, 1.4, 0.7), "##++..@@%%::"),
                ("head", (0, 1.25, 0), (0.95, 0.75, 0.8), "@@##++**%%=="),
                ("left-eye", (-0.24, 1.32, -0.45), (0.16, 0.16, 0.15), "@@@@@@@@@@@@"),
                ("right-eye", (0.24, 1.32, -0.45), (0.16, 0.16, 0.15), "@@@@@@@@@@@@"),
                ("left-leg", (-0.36, -0.95, 0), (0.38, 0.7, 0.45), "##++..@@%%::"),
                ("right-leg", (0.36, -0.95, 0), (0.38, 0.7, 0.45), "##++..@@%%::"),
                ("left-arm", (-0.92, 0.1, 0), (0.4, 1.1, 0.45), "##++..@@%%::"),
                ("right-arm", (0.92, 0.1, 0), (0.4, 1.1, 0.45), "##++..@@%%::"),
            ]
            for args in pieces:
                add_box(engine, *args)
            angle = seconds * 0.65
            eye = (
                5.8 * math.sin(angle),
                2.1 + math.sin(seconds * 0.4) * 0.5,
                -5.8 * math.cos(angle),
            )
            target = (0, 0, 0)
        else:
            # Checker tiles and unequal pillars make parallax and occlusion visible.
            for z in range(5):
                for x in range(-2, 3):
                    glyph = "." if (x + z) % 2 else ":"
                    add_box(
                        engine,
                        f"tile-{x}-{z}",
                        (x * 1.4, -1.1, z * 1.8),
                        (1.35, 0.12, 1.75),
                        glyph * 12,
                    )
            for i, (x, z, pillar_height) in enumerate(
                (
                    (-1.7, 0, 1.6),
                    (1.6, 1.5, 2.5),
                    (-1.5, 3.5, 3.1),
                    (1.5, 5.3, 1.8),
                    (0, 7, 3.5),
                )
            ):
                add_box(
                    engine,
                    f"pillar-{i}",
                    (x, pillar_height / 2 - 1, z),
                    (0.8, pillar_height, 0.8),
                    "##++..@@%%::",
                )
            eye = (
                2.3 * math.sin(seconds * 0.6),
                1.3,
                -4.8 + 1.4 * math.sin(seconds * 0.4),
            )
            target = (0, 0.15, 3.2)
        camera = engine.create_camera(
            (width, height), ratio=width * 0.5 / height, fov=math.radians(52)
        )
        camera.set_transformation(look_at(eye, target))
        return engine.render_cells(
            camera, fg=(117, 226, 218) if mode == "orbit" else (239, 192, 130)
        )
