"""A phosphor radar sweep with rings and fixed targets."""

from .effects import radar as frame
from .common import run

if __name__ == "__main__":
    run(frame, __doc__)
