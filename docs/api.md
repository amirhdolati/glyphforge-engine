# API guide

## Shared frame contract

A frame is a top-to-bottom rectangular sequence of rows. Each row contains cells:

```python
(character, (red, green, blue), (background_red, background_green, background_blue))
```

Each character must be printable single-column ASCII, from space through `~`; each color channel is an integer in 0–255. `glyphforge.frame.validate(frame)` checks the contract and returns immutable rows. Export functions validate their input. The low-level ANSI encoder trusts callers for speed: validate untrusted frames before passing them to it.

| Function | Purpose |
| --- | --- |
| `from_text(text, fg=..., bg=...)` | Pad text lines and make a validated cell frame |
| `to_text(frame)` | Plain characters separated by newlines |
| `to_html(frame, title=...)` | Standalone HTML with escaped text and inline color runs |
| `to_svg(frame, title=..., cell_width=9, cell_height=18)` | Standalone vector rendering of cells |
| `save_frame(frame, path)` | Write `.html`, `.svg`, `.ans`, or `.txt`; create parent directories |

SVG text uses the viewer's monospace font, so glyph appearance can vary. PNG/GIF generation is a documentation tool rather than a runtime dependency.

## Grid ray caster

### Scene and geometry

- `Scene(width=48, height=48, seed=17)` creates a rectangular map. `tiles`, `walls`, and `glow` are row-major `[y][x]` grids.
- `Building(x0, y0, x1, y1, height=6, color=..., sign="", neon=..., seed=0)` describes an axis-aligned solid and its procedural facade.
- `scene.add_building(building)` validates bounds and overlap and registers its occupancy ID. Do not mutate a registered footprint; occupancy is baked at registration.
- `Sprite(x, y, kind="tree", color=..., ...)` is an upright billboard. Add it to `scene.props`. Built-ins are `tree`, `lamp`, `bench`, `flowers`, `fountain`, `rail`, `stall`, `person`, `car`, and `boat`.
- `scene.add_light(x, y, radius=5, intensity=1)` bakes radial ground illumination. Moving a lamp sprite does not move its baked light.

Tiles: `r` road, `p` paving, `g` grass, `b` bridge, `w` water. Direct tile and glow edits are supported. Preserve grid shape and use supported tile names. Scene objects are mutable and owned by the application.

### Camera and environment

`View(scene, x=2.5, y=2.5, angle=0, ...)` holds one render snapshot. The scene is exposed as `view.city` for compatibility with the extracted renderer.

| Field | Units / contract |
| --- | --- |
| `x`, `y` | Ground coordinates inside scene bounds, outside solids |
| `angle` | Radians; zero looks toward +X, positive turns toward +Y |
| `pitch` | Horizon offset as a fraction of screen height |
| `eye_height` | World units; default 1.72 |
| `camera_fov` | Horizontal degrees in `[1, 179)`; default 76 |
| `clock` | Hours, normally `[0, 24)` |
| `time` | Animation seconds; advance explicitly |
| `weather` | 0 clear, 1 rain, 2 storm, 3 mist |
| `cloud`, `rain`, `wet` | Independent intensity values in `[0, 1]` |
| `lantern` | Enable camera-local light |
| `bob` | Camera motion offset in world units |
| `show_names` | Show sprite name/activity labels |
| `night_contrast` | Night appearance adjustment, clamped to 0.5–2 |
| `storm_flash_enabled` | Enables or disables storm flashes |

Use finite numeric inputs. Environment fields are not a weather simulation: setting `weather=1` alone does not increase rain or wetness.

### Renderer

`Renderer(cols, rows, aspect=0.5, sprite_art=None).render(view)` returns a fresh mutable cell grid. `aspect` is terminal-cell width divided by height. Keep a renderer across frames to retain sprite LOD hysteresis; recreate it on resize. The renderer stores intermediate state and is not safe for concurrent calls.

`renderer.depth` and `renderer.surface` expose the latest per-cell depth and building ID buffers for debugging. `-1` means no building surface. These are implementation diagnostics, not a stable plugin interface.

Register custom billboard art without changing global dictionaries:

```python
from glyphforge import Renderer, Sprite

scene.props.append(Sprite(8, 8, "beacon"))
renderer = Renderer(100, 36, sprite_art={
    "beacon": ((" /\\ ", "<@@>", " \\/ "), 1.5, 2.5),
})
```

Each art entry is `(tuple_of_ASCII_rows, world_width, world_height)`. Use non-empty rows and positive dimensions. Unknown kinds raise `KeyError`. Built-in shader branches still apply when overriding a built-in kind.

## Triangle backend

`MeshEngine` wraps the vendored RendASCII pipeline. It is left handed, with +Z forward and +Y up.

| Method | Contract |
| --- | --- |
| `create_camera((cols, rows), near=.1, far=100, fov=..., ratio=1, fog_char=" ", culling=True)` | FOV in radians; ratio is viewport world width/height; for 0.5 cell aspect use `cols * .5 / rows` |
| `add_mesh(name, vertices, triangles, glyphs=None)` | XYZ triples, zero-based index triples, one printable glyph per face; returns an instance |
| `instance.set_transformation(matrix)` | Local-to-world homogeneous transform |
| `camera.set_transformation(matrix)` | World-to-view transform |
| `instance.hide()` / `unhide()` | Toggle visibility |
| `render_cells(camera, fg=..., bg=...)` | Top-down shared RGB cell frame |
| `render_frame(camera, overlay=None, as_str=False)` | Inherited API; tuple output is bottom-up, string output is top-down |
| `load_model(name, filename, right_handed=False)` | Load a triangulated OBJ from `model_dir`, using materials from `material_dir` |
| `load_colormap(name, filename)` | JSON RGB-hex-to-character map from `colormap_dir` |
| `create_model_instance(model_name, colormap_name)` | Instantiate a previously loaded asset |
| `load_sprite(name, filename)` | Load an ASCII P3 PPM sprite from `sprite_dir` |
| `create_sprite_instance(sprite_name, colormap_name)` | Create a camera-facing PPM billboard |
| `close()` | Close/join optional worker processes |

`culling=False` disables side-frustum clipping in the inherited implementation; it does **not** disable back-face culling. Triangle winding matters. The cube example supplies working face winding.

`glyphforge.mesh.matrix` exposes `IDENTITY_H`, `compose(a,b)`, `translation_h((x,y,z))`, `rotation_h(radians, unit_axis)`, and uniform `scaling_h(scale)`. Composition applies the right-hand matrix first.

### Asset constraints

OBJ faces must already be triangulated and use positive one-based vertex indices. Provide `mtllib`, `usemtl`, and matching `Kd` diffuse colors. Textures, normals, UVs, negative indices, arbitrary polygons and material effects are not supported. The JSON colormap keys are lowercase six-digit RGB hex. An empty mapped value means transparency; otherwise the inherited loader uses its first character. Use printable ASCII.

PPM input is text P3 with RGB samples in 0–255 and maximum value 255. The loader does not decode binary P6. Assets should be trusted project files; this loader is not a hardened arbitrary-file parser.

## ANSI and terminal transport

`glyphforge.ansi.encode(frame, truecolor=True, x=1, y=1)` uses 1-based terminal coordinates. `encode_delta(previous, current, ...)` emits changed spans; a missing previous frame or shape mismatch emits a full frame. `FrameSnapshot.encode` caches a frame and invalidates on shape, color mode, or origin changes. `invalidate()` forces a full redraw. Changes outside the current frame's extent require an explicit terminal clear.

Use `Terminal(truecolor=None)` as a main-thread context manager. `None` enables environment-based color detection. Methods:

- `size()` returns `(columns, rows)`.
- `aspect()` returns a detected width/height ratio or 0.5.
- `events()` returns parsed events without blocking.
- `draw(frame, x=1, y=1, delta=False)` writes a synchronized update.
- `clear()` clears the screen and invalidates delta state.
- `mouse(enabled)` toggles motion reports.

Delta updates assume that every previous write reached the terminal and no other writer changes its contents. Call `clear()` after resize or outside writes. There is no terminal acknowledgement protocol.

`glyphforge.input.Input.feed(bytes, now=None)` incrementally parses ASCII/ANSI input. Events expose `key`, `shift`, `release`, `repeat`, `enhanced`, and optional `mouse=(column,row)`. Arrow keys are named `up/down/left/right`, and space is `space`; game movement bindings belong to your application. Escape and Ctrl-C produce `exit`. Enhanced terminals can report release events; legacy terminals cannot. The parser is intentionally not a full Unicode, IME, or clipboard input system.
