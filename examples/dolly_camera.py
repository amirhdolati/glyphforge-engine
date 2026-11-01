"""Move a camera through a fixed triangle scene to reveal parallax and occlusion."""

from .camera_scenes import render
from .common import run


def frame(width, height, seconds):
    return render(width, height, seconds, "dolly")


if __name__ == "__main__":
    run(frame, __doc__)
