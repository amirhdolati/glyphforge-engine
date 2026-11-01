"""A daytime street with variable-height buildings, glass and billboards."""

import math
from glyphforge import Renderer
from .scenes import street
from .common import run

view = street()
renderers = {}


def frame(width, height, seconds):
    view.time = seconds
    view.angle = math.sin(seconds * 0.15) * 0.15
    key = (width, height)
    if key not in renderers:
        renderers.clear()
        renderers[key] = Renderer(width, height)
    return renderers[key].render(view)


if __name__ == "__main__":
    run(frame, __doc__)
