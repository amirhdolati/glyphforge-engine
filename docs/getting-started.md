# Getting started

## Choose a backend

Use `Renderer` for colored streets, terrain and billboard scenes. Use `MeshEngine` for triangle geometry. Use the cell-grid API alone for dashboards, particle systems, text effects, or a renderer of your own.

The installed library has no runtime dependencies. Development image generation needs Pillow; package building needs setuptools and build. Interactive terminal control is POSIX-only. Importing the package and exporting a still do not acquire a terminal.

## Build a grid scene

```python
from glyphforge import Building, Renderer, Scene, Sprite, View, save_frame

scene = Scene(40, 24)
scene.add_building(Building(12, 4, 20, 11, height=9, sign="CAFE"))
scene.props.append(Sprite(10, 12, "lamp"))
scene.props.append(Sprite(20, 14, "tree"))
scene.add_light(10, 12, radius=6)
view = View(scene, x=3, y=12, angle=0, clock=22)
view.weather, view.rain, view.wet, view.cloud = 1, 0.7, 1.0, 0.5
renderer = Renderer(100, 36, aspect=0.5)
save_frame(renderer.render(view), "output/first-scene.html")
```

The grid's X axis points along the view at angle zero; positive angles rotate toward +Y. Footprints use integer, half-open coordinates: `(12, 4, 20, 11)` occupies X 12–19 and Y 4–10. Height is a world-space value, independent of footprint size. Keep the camera inside the map and outside buildings. Applications own movement, collision and time advancement.

`aspect` is character-cell width divided by height. A typical value is 0.5. In a live terminal, `terminal.aspect()` attempts to detect it. Resolution is measured in characters, not pixels.

## Animate safely

```python
import time
from glyphforge import Terminal

with Terminal() as terminal:
    start = time.monotonic()
    size = None
    while True:
        tick = time.monotonic()
        if any(event.key in ("exit", "q") for event in terminal.events()):
            break
        cols, rows = terminal.size()
        current_size = (max(1, min(cols, 100)), max(1, min(rows - 1, 36)))
        if current_size != size:
            size = current_size
            renderer = Renderer(*size, aspect=terminal.aspect())
            terminal.clear()
        view.time = tick - start
        terminal.draw(renderer.render(view), delta=True)
        time.sleep(max(0, 1 / 24 - (time.monotonic() - tick)))
```

Use `terminal.events()` in raw mode. Do not use `input()` for application input inside the terminal context. `Terminal` restores termios, the cursor, wrapping, and the alternate screen on ordinary exit, exceptions, SIGTERM, and SIGHUP. Run the terminal context on the main thread. Uncatchable termination such as SIGKILL cannot run cleanup.

## Export and share

`save_frame(frame, path)` selects `.html`, `.svg`, `.ans`, or `.txt` from the extension. HTML and SVG preserve cell colors; text preserves characters only. View `.ans` using `cat output/frame.ans` in an ANSI terminal. These files contain cursor-positioning sequences, so they are intended as terminal output rather than plain text documents.

```sh
python -m examples.night_rain --width 120 --height 40 --time 2 --output output/rain.html
python -m examples.rotating_cube --time 0.7 --output output/cube.svg
python -m examples.hello_terminal --256
```

## Build a triangle mesh

See [rotating_cube.py](../examples/rotating_cube.py) for complete geometry. `MeshEngine.add_mesh` takes XYZ vertices, index triples and one glyph per triangle. Apply local-to-world matrices with `instance.set_transformation`. A mesh camera looks along +Z with +Y up, unlike the grid camera's XY ground plane. Camera transformations are world-to-view matrices.

Use the engine as a context manager, especially when supplying `num_workers`, so worker processes are closed and joined. Keep multiprocessing entry points behind `if __name__ == "__main__":`.
