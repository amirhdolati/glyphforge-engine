"""A moving-camera 3D spacecraft study built from triangle meshes."""

from .showcase_3d import render
from .common import run


def frame(width, height, seconds):
    return render(width, height, seconds, "spacecraft")


if __name__ == "__main__":
    run(frame, __doc__)
