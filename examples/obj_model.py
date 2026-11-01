"""Load a triangulated OBJ with MTL diffuse-color-to-character mapping."""

from pathlib import Path
from glyphforge import MeshEngine
from glyphforge.mesh import matrix
from .common import run


def frame(width, height, seconds):
    assets = str(Path(__file__).parent / "assets")
    with MeshEngine(
        model_dir=assets, material_dir=assets, colormap_dir=assets
    ) as engine:
        engine.load_model("pyramid", "pyramid.obj")
        engine.load_colormap("palette", "palette.json")
        model = engine.create_model_instance("pyramid", "palette")
        model.set_transformation(
            matrix.compose(
                matrix.translation_h((0, 0, 4)),
                matrix.rotation_h(seconds * 0.5, (0, 1, 0)),
            )
        )
        camera = engine.create_camera((width, height), ratio=width * 0.5 / height)
        return engine.render_cells(camera, fg=(243, 185, 114))


if __name__ == "__main__":
    run(frame, __doc__)
