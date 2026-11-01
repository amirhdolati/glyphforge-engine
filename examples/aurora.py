"""Polar curtains of light and a deterministic star field."""

from .effects import aurora as frame
from .common import run

if __name__ == "__main__":
    run(frame, __doc__)
