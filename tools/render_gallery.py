"""Generate documentation images from actual engine frames (Pillow required)."""

import argparse
import importlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from glyphforge import save_frame

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/images"
from examples.catalog import NAMES


def raster(frame):
    # Pillow's bundled font makes this work without machine-specific font paths.
    font = ImageFont.load_default(size=14)
    image = Image.new("RGB", (len(frame[0]) * 10, len(frame) * 20), "#0a111c")
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(frame):
        for x, (char, fg, bg) in enumerate(row):
            draw.rectangle((x * 10, y * 20, x * 10 + 9, y * 20 + 19), fill=bg)
            draw.text((x * 10, y * 20 + 2), char, font=font, fill=fg)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", nargs="+", choices=NAMES, help="Regenerate selected examples"
    )
    args = parser.parse_args()
    selected = args.only or NAMES
    OUT.mkdir(parents=True, exist_ok=True)
    for name in selected:
        module = importlib.import_module("examples." + name)
        frame = module.frame(100, 36, 1)
        save_frame(frame, OUT / (name + ".svg"))
        raster(frame).save(OUT / (name + ".png"))
        print(name)
    for name in (
        "rotating_cube",
        "wormhole",
        "lava_lamp",
        "starflight",
        "torus_sculpture",
        "orbit_camera",
        "dolly_camera",
        "spacecraft_flyby",
        "suspension_bridge",
        "solar_orrery",
        "kinetic_tower",
    ):
        module = importlib.import_module("examples." + name)
        if name not in selected:
            continue
        count = 64 if name in ("orbit_camera", "dolly_camera") else 40
        frames = (
            [raster(module.frame(80, 30, index * 0.15)) for index in range(count)]
            if count == 64
            else [raster(module.frame(64, 24, index * 0.15)) for index in range(count)]
        )
        frames[0].save(
            OUT / (name + ".gif"),
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        print(name + ".gif")


if __name__ == "__main__":
    main()
