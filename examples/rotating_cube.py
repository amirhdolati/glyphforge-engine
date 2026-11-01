"""True triangle rasterization with the RendASCII-derived mesh backend."""

from glyphforge import MeshEngine
from glyphforge.mesh import matrix
from .common import run

VERTICES = (
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
)
TRIANGLES = (
    (0, 2, 1),
    (0, 3, 2),
    (4, 5, 6),
    (4, 6, 7),
    (0, 1, 5),
    (0, 5, 4),
    (3, 7, 6),
    (3, 6, 2),
    (1, 2, 6),
    (1, 6, 5),
    (0, 4, 7),
    (0, 7, 3),
)


def frame(width, height, seconds):
    with MeshEngine() as engine:
        camera = engine.create_camera((width, height), ratio=width * 0.5 / height)
        cube = engine.add_mesh("cube", VERTICES, TRIANGLES, "##++..@@%%::")
        rotation = matrix.compose(
            matrix.rotation_h(seconds * 0.7, (0, 1, 0)),
            matrix.rotation_h(0.35, (1, 0, 0)),
        )
        cube.set_transformation(
            matrix.compose(matrix.translation_h((0, 0, 4)), rotation)
        )
        return engine.render_cells(camera)


if __name__ == "__main__":
    run(frame, __doc__)
