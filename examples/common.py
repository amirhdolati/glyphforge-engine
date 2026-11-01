"""Shared live/offline runner; application policy belongs in examples."""

import argparse
import time
from glyphforge import Terminal, save_frame


def run(make_frame, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--output", help="Export .html/.svg/.ans/.txt instead of opening a TTY"
    )
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument(
        "--time", type=float, default=1.0, help="Animation seconds for a still"
    )
    parser.add_argument("--fps", type=float, default=24)
    parser.add_argument("--256", dest="palette256", action="store_true")
    args = parser.parse_args()
    if args.width < 1 or args.height < 1 or args.fps <= 0:
        parser.error("width, height and fps must be positive")
    if args.output:
        path = save_frame(make_frame(args.width, args.height, args.time), args.output)
        print(path)
        return
    with Terminal(truecolor=False if args.palette256 else None) as terminal:
        start = time.monotonic()
        previous_size = None
        while True:
            tick = time.monotonic()
            if any(
                event.key in ("exit", "q", "x") and not event.release
                for event in terminal.events()
            ):
                break
            width, height = terminal.size()
            width, height = (
                max(1, min(width, args.width)),
                max(1, min(height - 1, args.height)),
            )
            if previous_size != (width, height):
                terminal.clear()
                previous_size = (width, height)
            terminal.draw(make_frame(width, height, tick - start), delta=True)
            time.sleep(max(0, 1 / args.fps - (time.monotonic() - tick)))
