"""Parametric mesh examples using the inherited triangle rasterizer."""

import math
from glyphforge import MeshEngine
from glyphforge.mesh import matrix


def sculpture(width, height, seconds, kind):
    vertices = []
    faces = []
    if kind == "torus":
        nu, nv = 24, 10
        for i in range(nu):
            u = math.tau * i / nu
            for j in range(nv):
                v = math.tau * j / nv
                vertices.append(
                    (
                        (1 + 0.38 * math.cos(v)) * math.cos(u),
                        (0.38 * math.sin(v)),
                        (1 + 0.38 * math.cos(v)) * math.sin(u),
                    )
                )
        for i in range(nu):
            for j in range(nv):
                a = i * nv + j
                b = ((i + 1) % nu) * nv + j
                c = ((i + 1) % nu) * nv + (j + 1) % nv
                d = i * nv + (j + 1) % nv
                faces.extend(((a, b, c), (a, c, d)))
    else:
        n = 16
        for y in range(n):
            for x in range(n):
                xx = (x / (n - 1) - 0.5) * 3
                zz = (y / (n - 1) - 0.5) * 3
                yy = (
                    0.32 * math.sin(xx * 3 + seconds) * math.cos(zz * 3 - seconds * 0.7)
                )
                vertices.append((xx, yy, zz))
        for y in range(n - 1):
            for x in range(n - 1):
                a = y * n + x
                b = a + 1
                c = a + n + 1
                d = a + n
                faces.extend(((a, c, b), (a, d, c)))
    # Double-sided art so the sculpture remains visible from either side.
    faces = faces + [tuple(reversed(f)) for f in faces]
    glyphs = tuple(".,:+=*#@"[(i // 2) % 8] for i in range(len(faces)))
    with MeshEngine() as engine:
        camera = engine.create_camera((width, height), ratio=width * 0.5 / height)
        mesh = engine.add_mesh(kind, vertices, faces, glyphs)
        transform = matrix.compose(
            matrix.translation_h((0, 0, 4.4)),
            matrix.compose(
                matrix.rotation_h(0.7, (1, 0, 0)),
                matrix.rotation_h(seconds * 0.35, (0, 1, 0)),
            ),
        )
        mesh.set_transformation(transform)
        return engine.render_cells(
            camera, fg=(238, 165, 110) if kind == "torus" else (104, 225, 204)
        )
