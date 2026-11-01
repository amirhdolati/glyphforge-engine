"""A deterministic flight through a field of bright stars."""

from .effects import starflight as frame
from .common import run

if __name__ == "__main__":
    run(frame, __doc__)
