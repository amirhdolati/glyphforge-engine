# Architecture

```text
Application / examples
  ├── Scene + View ──> raycast.Renderer ──┐
  ├── triangles ────> MeshEngine ─────────┤
  └── custom graphics ───────────────────┤
                                        v
                      (ASCII character, foreground RGB, background RGB)
                                        │
                 ┌──────────────────────┴───────────────────┐
                 v                                          v
         ANSI / delta encoder                     HTML / SVG / text
                 │
         POSIX Terminal + Input
```

## Layout

```text
src/glyphforge/
  scene.py             Explicit scene, building, sprite and view records
  frame.py             Cell contract and portable exporters
  ansi.py              Full-frame and changed-span encoders
  input.py             Incremental terminal event parser
  terminal.py          Terminal lifecycle and output transport
  mesh.py              Public facade over the inherited triangle engine
  raycast/
    renderer.py        Projection, traversal, depth and compositing
    materials.py       Procedural shading, fog and reflection helpers
    sprites.py         Built-in billboard art
    interiors.py       Furnished window views
  _vendor/rendascii/    Namespaced upstream geometry/rasterization code
examples/              Demo content, geometry and a shared event loop
tests/                 Rendering, output and real PTY regression checks
tools/                 Reproducible documentation gallery
```

## Module boundaries

Applications own scene construction and frame pacing. Rendering, cell encoding, input parsing and terminal transport are separate modules. Importing the library does not acquire a terminal or start an animation loop. Source attribution and license notices are recorded in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Rendering passes

The ray caster computes a camera basis and atmospheric palette, renders sky and ground, traverses the occupancy grid using DDA, shades variable-height wall spans, applies light reflections, projects signs and depth-tested sprites, then overlays weather. Procedural urban materials are the defaults. It is stateful per renderer and intended for sequential frame calls.

The mesh path retains the RendASCII vertex, polygon and fragment stages. It transforms vertices, clips polygons, interpolates depth and resolves character fragments. The public facade converts its bottom-up character grid into the shared top-down RGB frame contract.

ANSI output is independent of either renderer. The input parser returns generic events, while applications choose movement bindings and frame pacing. Exporters do not touch terminal state.

## Current boundaries

The grid backend is 2.5D and has fixed view/sprite distances of 78 and 48 world units respectively. Custom sprites are supported, while facade/ground shaders remain procedural urban shaders. Mesh colors become characters; `render_cells` supplies a uniform foreground/background for that backend. Neither backend provides physics, scene serialization, a general material graph, or a GPU path.

The public API is version 0.1.0 and may evolve before 1.0. `_vendor` modules and renderer diagnostic buffers are implementation details. Future work can add general material callbacks and a scene protocol while preserving the shared cell format.
