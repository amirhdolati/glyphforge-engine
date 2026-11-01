"""An animated Mandelbrot study with escape-time shading."""

from .effects import mandelbrot as frame
from .common import run

if __name__ == "__main__":
    run(frame, __doc__)
