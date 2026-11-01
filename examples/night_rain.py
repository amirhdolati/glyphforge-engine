"""Wet pavement, neon windows, rain and baked pools of warm light."""

from . import raycast_street
from .common import run


def frame(width, height, seconds):
    view = raycast_street.view
    view.clock, view.weather, view.cloud, view.rain, view.wet = 22, 1, 0.55, 0.8, 1
    return raycast_street.frame(width, height, seconds)


if __name__ == "__main__":
    run(frame, __doc__)
