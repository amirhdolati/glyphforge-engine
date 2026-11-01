"""Animated torus geometry rendered with the triangle backend."""

from .mesh_sculptures import sculpture
from .common import run


def frame(width, height, seconds):
    return sculpture(width, height, seconds, "torus")


if __name__ == "__main__":
    run(frame, __doc__)
