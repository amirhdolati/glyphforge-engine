"""Generate documentation images from actual engine frames (Pillow required)."""

import importlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from glyphforge import save_frame

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/images"
NAMES = (
    "hello_terminal",
    "raycast_street",
    "sprite_garden",
    "rotating_cube",
    "obj_model",
    "night_rain",
)


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
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        module = importlib.import_module("examples." + name)
        frame = module.frame(100, 36, 1)
        save_frame(frame, OUT / (name + ".svg"))
        raster(frame).save(OUT / (name + ".png"))
        print(name)
    module = importlib.import_module("examples.rotating_cube")
    frames = [raster(module.frame(64, 24, index * 0.15)) for index in range(40)]
    frames[0].save(
        OUT / "rotating_cube.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
    )


if __name__ == "__main__":
    main()
