"""Billboard sprites, distance fog, vegetation and a non-square grid."""

import math
from glyphforge import Renderer
from .scenes import garden
from .common import run

view = garden()


def frame(width, height, seconds):
    view.time = seconds
    view.angle = math.sin(seconds * 0.2) * 0.15
    return Renderer(width, height).render(view)


if __name__ == "__main__":
    run(frame, __doc__)
