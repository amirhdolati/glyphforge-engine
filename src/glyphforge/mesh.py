"""Public facade over the MIT RendASCII-derived triangle pipeline."""

import math
from ._vendor.rendascii.interface import Engine as _Engine
from ._vendor.rendascii.geometry import matrix
from .frame import from_text


class MeshEngine(_Engine):
    """Triangle rasterization, OBJ/MTL and PPM sprites. Use as a context manager.

    Coordinates are left handed, +Z forward, +Y up. Model transforms are
    local-to-world; camera transforms are world-to-view. FOV is radians.
    """

    def __enter__(self):
        return self

    def close(self):
        if self._workers is not None:
            self._workers.close()
            self._workers.join()
            self._workers = None

    def __exit__(self, *args):
        self.close()

    def create_camera(
        self,
        resolution,
        near=0.1,
        far=100.0,
        fov=math.radians(70),
        ratio=1.0,
        fog_char=" ",
        culling=True,
    ):
        if len(resolution) != 2 or any(
            not isinstance(v, int) or v <= 0 for v in resolution
        ):
            raise ValueError("Resolution must be two positive integers")
        if not all(math.isfinite(v) for v in (near, far, fov, ratio)) or not (
            0 < near < far and 0 < fov < math.pi and ratio > 0
        ):
            raise ValueError("Require 0 < near < far, 0 < fov < pi and ratio > 0")
        if len(fog_char) != 1 or not " " <= fog_char <= "~":
            raise ValueError("fog_char must be printable ASCII")
        return super().create_camera(
            resolution, near, far, fov, ratio, fog_char, culling
        )

    def add_mesh(self, name, vertices, triangles, glyphs=None):
        """Register in-memory geometry and return its first transformable instance."""
        vertices = tuple(tuple(v) for v in vertices)
        triangles = tuple(tuple(t) for t in triangles)
        if not vertices or any(
            len(v) != 3 or not all(math.isfinite(c) for c in v) for v in vertices
        ):
            raise ValueError("Vertices must be finite xyz triples")
        if any(
            len(t) != 3
            or any(not isinstance(i, int) or i < 0 or i >= len(vertices) for i in t)
            for t in triangles
        ):
            raise ValueError("Triangles require three valid zero-based vertex indices")
        glyphs = tuple(glyphs) if glyphs is not None else ("#",) * len(triangles)
        if len(glyphs) != len(triangles) or any(
            len(g) != 1 or not " " <= g <= "~" for g in glyphs
        ):
            raise ValueError("Provide one printable ASCII glyph per triangle")
        keys = tuple(str(i) for i in range(len(triangles)))
        self._models[name] = vertices, triangles, keys
        self._colormaps[name] = dict(zip(keys, glyphs))
        return self.create_model_instance(name, name)

    def render_cells(self, camera, fg=(112, 224, 208), bg=(10, 17, 28)):
        """Convert the rasterizer's bottom-up glyph buffer to top-down RGB cells."""
        return from_text(self.render_frame(camera, as_str=True), fg, bg)


__all__ = ["MeshEngine", "matrix"]


def look_at(eye, target, up=(0.0, 1.0, 0.0)):
    """Return a left-handed world-to-view matrix for a camera at eye.

    The camera looks along +Z toward target. up defines the vertical direction;
    it must not be parallel to the viewing direction. Inputs are finite triples.
    """
    if any(
        len(v) != 3 or not all(math.isfinite(c) for c in v) for v in (eye, target, up)
    ):
        raise ValueError("eye, target and up must be finite XYZ triples")

    def unit(v):
        length = math.sqrt(sum(c * c for c in v))
        if length < 1e-12:
            raise ValueError(
                "Camera direction and up must define distinct, nonparallel axes"
            )
        return tuple(c / length for c in v)

    def cross(a, b):
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    forward = unit(tuple(t - e for t, e in zip(target, eye)))
    right = unit(cross(unit(up), forward))
    vertical = cross(forward, right)
    return tuple(
        tuple(axis) + (-sum(a * e for a, e in zip(axis, eye)),)
        for axis in (right, vertical, forward)
    ) + ((0.0, 0.0, 0.0, 1.0),)


__all__.append("look_at")
