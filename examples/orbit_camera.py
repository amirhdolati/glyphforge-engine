"""Orbit a stationary 3D robot sculpture with a world-to-view camera transform."""

from .camera_scenes import render
from .common import run


def frame(width, height, seconds):
    return render(width, height, seconds, "orbit")


if __name__ == "__main__":
    run(frame, __doc__)
