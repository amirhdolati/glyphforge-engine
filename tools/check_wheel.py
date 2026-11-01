"""Run with python -I after installing the built wheel, outside the source tree."""

from importlib.metadata import distribution
from importlib.resources import files
import tempfile
from pathlib import Path
from glyphforge import Building, MeshEngine, Renderer, Scene, View, save_frame
from glyphforge.mesh import look_at


def main():
    dist = distribution("glyphforge-engine")
    assert all("extra ==" in req for req in (dist.requires or [])), (
        "Unexpected runtime dependency"
    )
    assert files("glyphforge._vendor.rendascii").joinpath("LICENSE.txt").is_file()
    scene = Scene(20, 12)
    scene.add_building(Building(8, 2, 12, 8, sign="TEST"))
    frame = Renderer(40, 16).render(View(scene, x=2, y=6))
    with tempfile.TemporaryDirectory() as folder:
        for suffix in (".html", ".svg", ".ans", ".txt"):
            path = save_frame(frame, Path(folder) / ("frame" + suffix))
            assert path.stat().st_size > 0
    with MeshEngine() as engine:
        engine.add_mesh(
            "triangle",
            [(-1, -1, 0), (0, 1, 0), (1, -1, 0)],
            [(0, 1, 2), (2, 1, 0)],
            ["#", "#"],
        )
        camera = engine.create_camera((40, 20))
        camera.set_transformation(look_at((0, 0, -4), (0, 0, 0)))
        assert "#" in engine.render_frame(camera, as_str=True)
    print("Installed wheel: metadata, licenses, both renderers and exporters OK")


if __name__ == "__main__":
    main()
