"""A spiraling neon tunnel drawn directly into terminal cells."""

from .effects import wormhole as frame
from .common import run

if __name__ == "__main__":
    run(frame, __doc__)
