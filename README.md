<div align="center">

# GlyphForge Engine

**Build worlds out of characters.**

A pure-Python terminal rendering library for colored ASCII scenes, triangle meshes, and custom character graphics.

[Getting started](docs/getting-started.md) · [API guide](docs/api.md) · [Examples](examples/README.md) · [Creative gallery](docs/gallery.md) · [Architecture](docs/architecture.md) · [Donate](#support)

![A rotating mesh rendered by GlyphForge](docs/images/rotating_cube.gif)

</div>

GlyphForge is a terminal rendering engine for 3D objects, atmospheric scenes, and character graphics. Create triangle meshes, position a camera in 3D space, and render perspective views directly to colored terminal cells. Use the same frame format for live animation and portable image exports.

**Python 3.10+ · No runtime dependencies · MIT · Alpha API**

## What it renders

- **Colored grid scenes:** variable-height buildings, depth-tested billboards, procedural facades, furnished window views, fog, day/night lighting, rain, and wet-ground reflections.
- **Triangle meshes:** transforms, perspective projection, clipping, depth testing, in-memory triangles, OBJ/MTL loading, and PPM billboards through the RendASCII-derived backend.
- **Any cell grid:** bring your own renderer and send `(character, foreground RGB, background RGB)` cells to the terminal.
- **Terminal output:** truecolor or xterm-256, full frames or changed spans, alternate-screen management, keyboard/mouse events, and terminal restoration.
- **Offline exports:** ANSI, HTML, SVG, and plain text without opening a terminal.

The grid renderer uses a 2.5D world of axis-aligned footprints and upright sprites. The mesh renderer supports actual 3D triangle geometry and maps material colors to characters. These are two distinct backends sharing a terminal cell format.

## Install and run

```sh
git clone https://github.com/amirhdolati/glyphforge-engine.git
cd glyphforge-engine
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m examples.night_rain
```

Press **Q**, **X**, **Escape**, or **Ctrl-C** to exit a demo. Interactive rendering requires macOS, Linux, or WSL with an ANSI terminal. Offline rendering does not require a TTY. Examples are run from the repository root.

Install the library directly from GitHub:

```sh
python -m pip install "git+https://github.com/amirhdolati/glyphforge-engine.git"
```

This repository does not imply a PyPI release. The distribution is named `glyphforge-engine`; the Python import is `glyphforge`.

## Real 3D objects and moving cameras

Create a mesh in world coordinates and move the camera around it. GlyphForge projects its triangles, resolves depth, and draws the visible surfaces as terminal characters. These demos keep the geometry stationary: the changing view comes from the camera itself.

### Orbit a 3D sculpture

![Moving camera orbiting a stationary robot sculpture](docs/images/orbit_camera.gif)

```sh
python -m examples.orbit_camera
```

The camera circles a robot made of solid boxes, revealing its front, sides, back, and top. Different face glyphs make the shape readable as perspective and occlusion change.

### Dolly and parallax

![Camera movement across a fixed scene of pillars](docs/images/dolly_camera.gif)

```sh
python -m examples.dolly_camera
```

The camera moves sideways and forward through a view of pillars and a tiled floor. Nearby objects shift more than distant objects, and surfaces hide one another according to depth.

```python
from glyphforge.mesh import look_at

# World-space camera position and the point it looks toward.
camera.set_transformation(look_at(eye=(4, 2, -6), target=(0, 0, 0)))
frame = engine.render_cells(camera)
```

[Moving-camera tutorial and coordinate conventions](docs/cameras.md) · [Orbit source](examples/orbit_camera.py) · [Dolly source](examples/dolly_camera.py)

## Your first scene

```python
from glyphforge import Building, Renderer, Scene, View, save_frame

scene = Scene(width=32, height=24)
scene.add_building(Building(10, 6, 18, 13, height=8, sign="HELLO"))
scene.add_light(9, 8, radius=7)

view = View(scene, x=3, y=9, clock=21, angle=0)
frame = Renderer(100, 36, aspect=0.5).render(view)
save_frame(frame, "output/hello.html")
```

Open the exported HTML in a browser. To display an existing frame interactively:

```python
import time
from glyphforge import Terminal

with Terminal() as terminal:
    terminal.draw(frame)
    time.sleep(3)
```

For a non-blocking animation loop with resizing and event handling, see [the shared example runner](examples/common.py).

## Gallery

Every preview below comes from the engine's actual character/color grid. PNG and GIF previews are rasterized by the reproducible [gallery tool](tools/render_gallery.py); the library also exports SVG directly.

### A street after dark

![Neon windows, rain and wet paving](docs/images/night_rain.png)

```sh
python -m examples.night_rain
python -m examples.night_rain --output output/night.html
```

### Daylight and depth

![Variable-height street buildings](docs/images/raycast_street.png)

```sh
python -m examples.raycast_street --output output/street.svg
```

### Billboard garden

![Trees, a fountain and garden furniture](docs/images/sprite_garden.png)

```sh
python -m examples.sprite_garden
```

### Meshes and character graphics

| OBJ / MTL model | A custom cell-grid effect |
| --- | --- |
| ![Pyramid mesh](docs/images/obj_model.png) | ![Animated character waves](docs/images/hello_terminal.png) |

```sh
python -m examples.rotating_cube
python -m examples.obj_model
python -m examples.hello_terminal
```

All 28 demos accept `--output`, `--width`, `--height`, `--time`, `--fps`, and `--256`. See the [example guide](examples/README.md).

## Project showcase: Glyph City

[**Glyph City: Afterlight**](https://github.com/amirhdolati/glyph-city) is a featured terminal graphics project: a living terminal city with autonomous residents, furnished shop windows, changing weather, canal reflections, and an optional first-person walking mode.

[![Glyph City — original City Watch GIF](https://raw.githubusercontent.com/amirhdolati/glyph-city/master/docs/media/city-watch.gif)](https://github.com/amirhdolati/glyph-city)

The original City Watch GIF above comes directly from the Glyph City repository and shows its canal scene and nighttime rain.

[Explore Glyph City](https://github.com/amirhdolati/glyph-city) · [Original GIF](https://github.com/amirhdolati/glyph-city/blob/master/docs/media/city-watch.gif)

## Twelve more creative directions

The gallery now has **28 runnable examples**. Explore procedural light, mathematical art, instruments, particles, new environments, and animated mesh sculptures.

| Aurora curtains | Neon wormhole |
| --- | --- |
| [![Aurora curtains](docs/images/aurora.png)](examples/aurora.py) | [![Neon wormhole](docs/images/wormhole.png)](examples/wormhole.py) |
| `python -m examples.aurora` | `python -m examples.wormhole` |

| Sunset ocean | Mandelbrot study |
| --- | --- |
| [![Sunset ocean](docs/images/sunset_ocean.png)](examples/sunset_ocean.py) | [![Mandelbrot study](docs/images/fractal_zoom.png)](examples/fractal_zoom.py) |
| `python -m examples.sunset_ocean` | `python -m examples.fractal_zoom` |

| Phosphor radar | Lava lamp |
| --- | --- |
| [![Phosphor radar](docs/images/radar_station.png)](examples/radar_station.py) | [![Lava lamp](docs/images/lava_lamp.png)](examples/lava_lamp.py) |
| `python -m examples.radar_station` | `python -m examples.lava_lamp` |

| Wave interference | Starflight |
| --- | --- |
| [![Wave interference](docs/images/wave_interference.png)](examples/wave_interference.py) | [![Starflight](docs/images/starflight.png)](examples/starflight.py) |
| `python -m examples.wave_interference` | `python -m examples.starflight` |

| Twilight canal | Fog monoliths |
| --- | --- |
| [![Twilight canal](docs/images/neon_canal.png)](examples/neon_canal.py) | [![Fog monoliths](docs/images/fog_monoliths.png)](examples/fog_monoliths.py) |
| `python -m examples.neon_canal` | `python -m examples.fog_monoliths` |

| Torus sculpture | Ripple terrain |
| --- | --- |
| [![Torus sculpture](docs/images/torus_sculpture.png)](examples/torus_sculpture.py) | [![Ripple terrain](docs/images/ripple_terrain.png)](examples/ripple_terrain.py) |
| `python -m examples.torus_sculpture` | `python -m examples.ripple_terrain` |

[Open the full gallery, animations, and source links →](docs/gallery.md)

## More 3D objects to explore

Spacecraft, architecture, orbital motion, crystal forms and kinetic sculpture—all rendered from triangle meshes with moving cameras.

| Spacecraft flyby | Castle courtyard |
| --- | --- |
| [![Spacecraft flyby](docs/images/spacecraft_flyby.png)](examples/spacecraft_flyby.py) | [![Castle courtyard](docs/images/castle_orbit.png)](examples/castle_orbit.py) |
| `python -m examples.spacecraft_flyby` | `python -m examples.castle_orbit` |

| Suspension bridge | Solar orrery |
| --- | --- |
| [![Suspension bridge](docs/images/suspension_bridge.png)](examples/suspension_bridge.py) | [![Solar orrery](docs/images/solar_orrery.png)](examples/solar_orrery.py) |
| `python -m examples.suspension_bridge` | `python -m examples.solar_orrery` |

| Spiral staircase | Tetrahedral sculpture |
| --- | --- |
| [![Spiral staircase](docs/images/spiral_staircase.png)](examples/spiral_staircase.py) | [![Tetrahedral sculpture](docs/images/molecule_orbit.png)](examples/molecule_orbit.py) |
| `python -m examples.spiral_staircase` | `python -m examples.molecule_orbit` |

| Crystal cluster | Kinetic tower |
| --- | --- |
| [![Crystal cluster](docs/images/crystal_cluster.png)](examples/crystal_cluster.py) | [![Kinetic tower](docs/images/kinetic_tower.png)](examples/kinetic_tower.py) |
| `python -m examples.crystal_cluster` | `python -m examples.kinetic_tower` |

[Full 3D gallery with animations and source links](docs/gallery.md#more-3d-objects-and-structures)

## Development

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pip install build ruff Pillow
ruff check src examples tests tools --select F
ruff format --check src examples tests tools
python -m build
PYTHONPATH=src:. python tools/render_gallery.py
```

Tests cover depth occlusion, rectangular maps, scene validation, custom sprites, example rendering, ANSI deltas, fragmented keyboard events, and real POSIX terminal restoration. CI tests Python 3.10–3.13 on Linux and Python 3.13 on macOS, and builds a wheel and source distribution.

## Scope and limitations

GlyphForge currently has an **alpha API**. The ray caster provides procedural urban materials; it is not a general shader system. Its view distance is 78 world units, sprites are culled at 48 units, and a camera should remain outside solid footprints. There is no physics or collision system. Use printable single-column ASCII, not wide Unicode or emoji. Full terminal frames are the default; delta output assumes exclusive screen ownership and requires invalidation after external writes. Native Windows interactive input is not implemented; use WSL.

The inherited OBJ loader expects triangulated faces and a material library with `Kd` colors covered by the colormap. It does not implement arbitrary OBJ features. See [API contracts](docs/api.md) before importing assets.

## Attribution

The triangle backend includes MIT-licensed RendASCII code by **Garrett Russell Fairburn**, copyright 2018–2020. Its original copyright and license are preserved in the package. See [third-party notices](THIRD_PARTY_NOTICES.md).

## Support

If GlyphForge helps your project, you can support development with a donation on **TRON**.

```text
TZ6HTiRLeyWoFJ5rGgx6qbMyjLAHNb6hfb
```

[View the donation address on TRONSCAN](https://tronscan.org/#/address/TZ6HTiRLeyWoFJ5rGgx6qbMyjLAHNb6hfb)

<img src="docs/images/donation-tron.png" alt="TRON donation QR code supplied by the project owner" width="280">

## License

[MIT](LICENSE), with the RendASCII copyright and license retained for the vendored backend.
