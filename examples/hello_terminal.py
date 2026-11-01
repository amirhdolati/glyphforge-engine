"""The cell-grid API without any 3D renderer."""

import math
from .common import run


def frame(width, height, seconds):
    rows = []
    ramp = " .:-=+*#%@"
    for y in range(height):
        row = []
        for x in range(width):
            wave = (math.sin(x * 0.12 + seconds) + math.cos(y * 0.25 - seconds) + 2) / 4
            row.append(
                (
                    ramp[min(9, int(wave * 10))],
                    (int(70 + 160 * wave), int(140 + 90 * wave), 210),
                    (10, 17, 28),
                )
            )
        rows.append(row)
    title = " GLYPHFORGE / CHARACTER GRAPHICS "
    for x, char in enumerate(title[:width]):
        rows[height // 2][x] = (char, (255, 210, 130), (22, 35, 48))
    return rows


if __name__ == "__main__":
    run(frame, __doc__)
