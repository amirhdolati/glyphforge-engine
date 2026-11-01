# Creative example gallery

Twenty-nine runnable examples explore three routes into GlyphForge: authored grid scenes, triangle meshes, and custom cell renderers. The procedural examples implement their own visual effects and use the engine for cell validation, terminal presentation, and export; these are not additional built-in 3D backends.

Run from the repository root after `python -m pip install -e .`. Every image below is generated from the corresponding example at 100 × 36 cells and time 1.0. Use `--output output/name.html` for a headless preview.

## Aurora curtains

**Procedural cells.** Layered green and violet light curtains under a sparse star field.

![Aurora curtains](images/aurora.png)

```sh
python -m examples.aurora
python -m examples.aurora --output output/aurora.html
```

[Source](../examples/aurora.py) · [Vector preview](images/aurora.svg)

## Neon wormhole

**Procedural cells.** Polar coordinates and inverse-radius stripes form a twisting tunnel.

![Neon wormhole](images/wormhole.png)

```sh
python -m examples.wormhole
python -m examples.wormhole --output output/wormhole.html
```

[Source](../examples/wormhole.py) · [Vector preview](images/wormhole.svg)

## Sunset ocean

**Procedural cells.** A warm sky, a low sun, moving waves and a narrow reflection path.

![Sunset ocean](images/sunset_ocean.png)

```sh
python -m examples.sunset_ocean
python -m examples.sunset_ocean --output output/sunset_ocean.html
```

[Source](../examples/sunset_ocean.py) · [Vector preview](images/sunset_ocean.svg)

## Mandelbrot study

**Procedural cells.** Escape-time iteration maps a slowly changing complex plane into colored glyphs.

![Mandelbrot study](images/fractal_zoom.png)

```sh
python -m examples.fractal_zoom
python -m examples.fractal_zoom --output output/fractal_zoom.html
```

[Source](../examples/fractal_zoom.py) · [Vector preview](images/fractal_zoom.svg)

## Phosphor radar

**Procedural cells.** A rotating sweep with persistence, range rings and fixed targets.

![Phosphor radar](images/radar_station.png)

```sh
python -m examples.radar_station
python -m examples.radar_station --output output/radar_station.html
```

[Source](../examples/radar_station.py) · [Vector preview](images/radar_station.svg)

## Lava lamp

**Procedural cells.** Six moving inverse-distance fields merge into soft glowing blobs.

![Lava lamp](images/lava_lamp.png)

```sh
python -m examples.lava_lamp
python -m examples.lava_lamp --output output/lava_lamp.html
```

[Source](../examples/lava_lamp.py) · [Vector preview](images/lava_lamp.svg)

## Wave interference

**Procedural cells.** Two radial sources produce moving bands of constructive and destructive interference.

![Wave interference](images/wave_interference.png)

```sh
python -m examples.wave_interference
python -m examples.wave_interference --output output/wave_interference.html
```

[Source](../examples/wave_interference.py) · [Vector preview](images/wave_interference.svg)

## Starflight

**Projected particles.** Deterministic stars expand from a vanishing point with distance-based brightness.

![Starflight](images/starflight.png)

```sh
python -m examples.starflight
python -m examples.starflight --output output/starflight.html
```

[Source](../examples/starflight.py) · [Vector preview](images/starflight.svg)

## Twilight canal

**Grid ray caster.** A water corridor with illuminated facades, street lamps and a billboard boat.

![Twilight canal](images/neon_canal.png)

```sh
python -m examples.neon_canal
python -m examples.neon_canal --output output/neon_canal.html
```

[Source](../examples/neon_canal.py) · [Vector preview](images/neon_canal.svg)

## Fog monoliths

**Grid ray caster.** Two rows of progressively taller structures recede into mist at dawn.

![Fog monoliths](images/fog_monoliths.png)

```sh
python -m examples.fog_monoliths
python -m examples.fog_monoliths --output output/fog_monoliths.html
```

[Source](../examples/fog_monoliths.py) · [Vector preview](images/fog_monoliths.svg)

## Torus sculpture

**Triangle mesh.** A parametric ring with a visible central opening and animated 3D transforms.

![Torus sculpture](images/torus_sculpture.png)

```sh
python -m examples.torus_sculpture
python -m examples.torus_sculpture --output output/torus_sculpture.html
```

[Source](../examples/torus_sculpture.py) · [Vector preview](images/torus_sculpture.svg)

## Ripple terrain

**Triangle mesh.** An animated height field rebuilt as triangles and viewed in perspective.

![Ripple terrain](images/ripple_terrain.png)

```sh
python -m examples.ripple_terrain
python -m examples.ripple_terrain --output output/ripple_terrain.html
```

[Source](../examples/ripple_terrain.py) · [Vector preview](images/ripple_terrain.svg)

## In motion

Four of the new demos also have reproducible animated previews. GIF uses a reduced palette; live truecolor output and SVG stills preserve more color detail.

### Wormhole

![Animated wormhole](images/wormhole.gif)

### Lava Lamp

![Animated lava_lamp](images/lava_lamp.gif)

### Starflight

![Animated starflight](images/starflight.gif)

### Torus Sculpture

![Animated torus_sculpture](images/torus_sculpture.gif)

## Moving cameras around real 3D geometry

The following scenes keep every mesh fixed in world coordinates. Only the camera moves.

### Robot orbit

![Camera orbiting a robot sculpture](images/orbit_camera.gif)

```sh
python -m examples.orbit_camera
```

[Source](../examples/orbit_camera.py) · [Still image](images/orbit_camera.png) · [Vector preview](images/orbit_camera.svg)

### Dolly through pillars

![Dolly camera and depth occlusion](images/dolly_camera.gif)

```sh
python -m examples.dolly_camera
```

[Source](../examples/dolly_camera.py) · [Still image](images/dolly_camera.png) · [Vector preview](images/dolly_camera.svg)

[Learn how the camera transforms work](cameras.md).

## More 3D objects and structures

Eight additional mesh studies use real triangle geometry and a moving camera. Run each from the repository root; every command also accepts `--output`, `--time`, and the standard size options.

### Spacecraft flyby

A low-poly spacecraft with swept wings, a raised cockpit, tail fins and engine details. The camera orbits the stationary mesh.

![Spacecraft flyby](images/spacecraft_flyby.png)

```sh
python -m examples.spacecraft_flyby
python -m examples.spacecraft_flyby --output output/spacecraft_flyby.html
```

[Source](../examples/spacecraft_flyby.py) · [SVG](images/spacecraft_flyby.svg)

![Animated Spacecraft flyby](images/spacecraft_flyby.gif)

### Castle courtyard

Four crenellated towers frame a courtyard and an open gateway. Moving viewpoints expose the walls, entrance and interior.

![Castle courtyard](images/castle_orbit.png)

```sh
python -m examples.castle_orbit
python -m examples.castle_orbit --output output/castle_orbit.html
```

[Source](../examples/castle_orbit.py) · [SVG](images/castle_orbit.svg)

### Suspension bridge

A deck, paired towers, suspension cables and vertical hangers form a small bridge viewed from a moving camera.

![Suspension bridge](images/suspension_bridge.png)

```sh
python -m examples.suspension_bridge
python -m examples.suspension_bridge --output output/suspension_bridge.html
```

[Source](../examples/suspension_bridge.py) · [SVG](images/suspension_bridge.svg)

![Animated Suspension bridge](images/suspension_bridge.gif)

### Solar orrery

Three faceted planets travel along visible orbital rings around a central sun. Object motion and camera motion run independently; this is an artistic model, not a scale-accurate simulation.

![Solar orrery](images/solar_orrery.png)

```sh
python -m examples.solar_orrery
python -m examples.solar_orrery --output output/solar_orrery.html
```

[Source](../examples/solar_orrery.py) · [SVG](images/solar_orrery.svg)

![Animated Solar orrery](images/solar_orrery.gif)

### Spiral staircase

Sixteen steps wrap around a central column. Each step has its own translation and rotation, with outer handrail posts.

![Spiral staircase](images/spiral_staircase.png)

```sh
python -m examples.spiral_staircase
python -m examples.spiral_staircase --output output/spiral_staircase.html
```

[Source](../examples/spiral_staircase.py) · [SVG](images/spiral_staircase.svg)

### Tetrahedral sculpture

A central octahedron connects to four outer shapes with solid bonds. This molecular-style sculpture is a geometry study, not a chemical simulation.

![Tetrahedral sculpture](images/molecule_orbit.png)

```sh
python -m examples.molecule_orbit
python -m examples.molecule_orbit --output output/molecule_orbit.html
```

[Source](../examples/molecule_orbit.py) · [SVG](images/molecule_orbit.svg)

### Crystal cluster

Seven hexagonal prisms rise to faceted tips, with a taller central crystal and smaller surrounding forms.

![Crystal cluster](images/crystal_cluster.png)

```sh
python -m examples.crystal_cluster
python -m examples.crystal_cluster --output output/crystal_cluster.html
```

[Source](../examples/crystal_cluster.py) · [SVG](images/crystal_cluster.svg)

### Kinetic tower

Nine square slabs twist at different angles while the camera circles the stack. The geometry demonstrates independent model and camera transforms.

![Kinetic tower](images/kinetic_tower.png)

```sh
python -m examples.kinetic_tower
python -m examples.kinetic_tower --output output/kinetic_tower.html
```

[Source](../examples/kinetic_tower.py) · [SVG](images/kinetic_tower.svg)

![Animated Kinetic tower](images/kinetic_tower.gif)

## Original examples

The original six demos remain available: [character waves](../examples/hello_terminal.py), [daylight street](../examples/raycast_street.py), [rainy night](../examples/night_rain.py), [sprite garden](../examples/sprite_garden.py), [rotating cube](../examples/rotating_cube.py), and [OBJ model](../examples/obj_model.py).

## Regeneration

```sh
python -m pip install Pillow
PYTHONPATH=src:. python tools/render_gallery.py
```

The tool generates 29 PNGs, 29 SVGs and twelve GIFs from actual frames. The Glyph City showcase uses its upstream GIF directly and is not regenerated here.

## Vaporwave horizon

**3D triangle scene.** A horizontally striped sunset sits behind a triangulated wireframe mountain range. A neon floor grid converges toward the horizon while the camera glides gently from side to side.

![Vaporwave sunset, wireframe mountains and perspective grid](images/vaporwave.png)

```sh
python -m examples.vaporwave
python -m examples.vaporwave --output output/vaporwave.html
```

![Animated vaporwave 3D scene](images/vaporwave.gif)

[Source](../examples/vaporwave.py) · [SVG preview](images/vaporwave.svg)
