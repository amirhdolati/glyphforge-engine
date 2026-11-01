"""Small, explicit scene objects; no gameplay or global map size."""

from __future__ import annotations
from dataclasses import dataclass, field
import math

Color = tuple[int, int, int]


@dataclass
class Building:
    """Axis-aligned footprint in grid cells, height in world units."""

    x0: int
    y0: int
    x1: int
    y1: int
    height: float = 6.0
    color: Color = (107, 151, 153)
    sign: str = ""
    neon: Color = (102, 229, 218)
    seed: int = 0


@dataclass
class Sprite:
    x: float
    y: float
    kind: str = "tree"
    color: Color = (190, 170, 140)
    phase: float = 0.0
    name: str = ""
    activity: str = ""
    umbrella: bool = False
    dialogue: str = ""


@dataclass
class Scene:
    """Rectangular grid. Tiles: r=road, p=paving, g=grass, b=bridge, w=water.

    Use add_building to keep occupancy and building IDs synchronized. Direct
    tile/glow edits are supported; keep the rectangular shape unchanged.
    """

    width: int = 48
    height: int = 48
    seed: int = 17
    buildings: list[Building] = field(default_factory=list, init=False)
    props: list[Sprite] = field(default_factory=list, init=False)
    tiles: list = field(init=False, repr=False)
    walls: list = field(init=False, repr=False)
    glow: list = field(init=False, repr=False)

    def __post_init__(self):
        if any(not isinstance(v, int) or v < 1 for v in (self.width, self.height)):
            raise ValueError("Scene dimensions must be positive integers")
        self.tiles = [["p"] * self.width for _ in range(self.height)]
        self.walls = [[-1] * self.width for _ in range(self.height)]
        self.glow = [[0.0] * self.width for _ in range(self.height)]

    def add_building(self, building: Building) -> Building:
        b = building
        if not all(isinstance(v, int) for v in (b.x0, b.y0, b.x1, b.y1)):
            raise ValueError("Building footprints must use integer grid coordinates")
        if not (0 <= b.x0 < b.x1 <= self.width and 0 <= b.y0 < b.y1 <= self.height):
            raise ValueError("Building footprint must be inside the scene")
        if not math.isfinite(b.height) or b.height <= 0:
            raise ValueError("Building height must be positive and finite")
        if any(
            self.walls[y][x] >= 0 for y in range(b.y0, b.y1) for x in range(b.x0, b.x1)
        ):
            raise ValueError("Building footprints cannot overlap")
        index = len(self.buildings)
        self.buildings.append(b)
        for y in range(b.y0, b.y1):
            for x in range(b.x0, b.x1):
                self.walls[y][x] = index
        return b

    def add_light(self, x: float, y: float, radius: float = 5, intensity: float = 1):
        """Bake a radial light into the ground grid (rendering does not move it)."""
        if (
            not all(math.isfinite(v) for v in (x, y, radius, intensity))
            or radius <= 0
            or intensity < 0
        ):
            raise ValueError(
                "Light parameters must be finite; radius > 0, intensity >= 0"
            )
        for yy in range(
            max(0, math.floor(y - radius)), min(self.height, math.ceil(y + radius) + 1)
        ):
            for xx in range(
                max(0, math.floor(x - radius)),
                min(self.width, math.ceil(x + radius) + 1),
            ):
                value = intensity * max(
                    0, 1 - math.hypot(xx + 0.5 - x, yy + 0.5 - y) / radius
                )
                self.glow[yy][xx] = min(1, self.glow[yy][xx] + value)


@dataclass
class View:
    """Camera and environment snapshot. Angles/pitch: radians / screen fraction.

    clock is hours [0,24), time is animation seconds. Weather is 0 clear,
    1 rain, 2 storm, 3 mist. cloud/rain/wet are independent intensities [0,1].
    """

    city: Scene
    x: float = 2.5
    y: float = 2.5
    angle: float = 0.0
    pitch: float = 0.0
    eye_height: float = 1.72
    camera_fov: float = 76.0
    clock: float = 14.0
    time: float = 0.0
    cloud: float = 0.0
    rain: float = 0.0
    wet: float = 0.0
    weather: int = 0
    bob: float = 0.0
    lantern: bool = False
    night_contrast: float = 1.0
    storm_flash_enabled: bool = True
    show_names: bool = False
