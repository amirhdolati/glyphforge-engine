import importlib
import unittest
from glyphforge import Building, MeshEngine, Renderer, Scene, Sprite, View, from_text
from glyphforge.ansi import FrameSnapshot, encode, dirty_spans
from glyphforge.frame import to_html, to_svg, validate
from glyphforge.input import Input
from glyphforge.mesh import matrix


class RenderingTests(unittest.TestCase):
    def test_rectangular_variable_height_occlusion(self):
        scene = Scene(30, 12)
        scene.add_building(Building(6, 4, 8, 8, height=3))
        scene.add_building(Building(12, 4, 14, 8, height=12))
        renderer = Renderer(60, 30)
        frame = renderer.render(View(scene, x=2, y=6))
        validate(frame)
        self.assertTrue(
            {0, 1}.issubset({bid for row in renderer.surface for bid in row})
        )
        self.assertEqual(renderer.render(View(scene, x=2, y=6)), frame)

    def test_scene_validation(self):
        with self.assertRaises(ValueError):
            Scene(0, 4)
        scene = Scene(12, 8)
        scene.add_building(Building(4, 2, 6, 4))
        for b in (
            Building(-1, 0, 3, 3),
            Building(4, 2, 6, 4),
            Building(1, 1, 2, 2, height=0),
        ):
            with self.assertRaises(ValueError):
                scene.add_building(b)
        for view in (View(scene, x=-1), View(scene, camera_fov=180)):
            with self.assertRaises(ValueError):
                Renderer(20, 10).render(view)
        with self.assertRaises(ValueError):
            Renderer(0, 10)

    def test_custom_billboard(self):
        scene = Scene(20, 12)
        scene.props.append(Sprite(6, 6, "beacon"))
        renderer = Renderer(60, 24, sprite_art={"beacon": (("@@@", " @ "), 2, 3)})
        frame = renderer.render(View(scene, x=2, y=6))
        self.assertTrue(any(c[0] == "@" for row in frame for c in row))

    def test_triangle_depth_and_behind_camera(self):
        with MeshEngine() as engine:
            camera = engine.create_camera((40, 20), ratio=1)
            vertices = ((-1, -1, 0), (0, 1, 0), (1, -1, 0))
            near = engine.add_mesh("near", vertices, ((0, 1, 2),), "N")
            far = engine.add_mesh("far", vertices, ((0, 1, 2),), "F")
            near.set_transformation(matrix.translation_h((0, 0, 3)))
            far.set_transformation(matrix.translation_h((0, 0, 5)))
            frame = engine.render_frame(camera, as_str=True)
            self.assertIn("N", frame)
            self.assertNotIn("F", frame)
            near.hide()
            self.assertIn("F", engine.render_frame(camera, as_str=True))
            far.set_transformation(matrix.translation_h((0, 0, -3)))
            self.assertFalse(engine.render_frame(camera, as_str=True).strip())

    def test_mesh_validation(self):
        with MeshEngine() as engine:
            with self.assertRaises(ValueError):
                engine.create_camera((0, 20))
            with self.assertRaises(ValueError):
                engine.create_camera((20, 20), near=2, far=1)
            with self.assertRaises(ValueError):
                engine.add_mesh("bad", ((0, 0, 0),), ((0, 1, 2),))

    def test_examples_at_multiple_sizes(self):
        for name in (
            "hello_terminal",
            "raycast_street",
            "sprite_garden",
            "rotating_cube",
            "obj_model",
            "night_rain",
        ):
            module = importlib.import_module("examples." + name)
            for w, h in ((1, 1), (32, 12), (80, 28)):
                with self.subTest(example=name, size=(w, h)):
                    frame = validate(module.frame(w, h, 1))
                    self.assertEqual((len(frame[0]), len(frame)), (w, h))


class OutputTests(unittest.TestCase):
    def test_delta_and_invalidation(self):
        old = from_text("ABCD\nEFGH")
        new = from_text("A CD\nEFZH")
        for rgb in (True, False):
            cache = FrameSnapshot()
            self.assertEqual(cache.encode(old, rgb), encode(old, rgb))
            self.assertEqual(cache.encode(old, rgb), "")
            delta = cache.encode(new, rgb)
            self.assertIn("\x1b[1;2H", delta)
            self.assertIn("\x1b[2;3H", delta)
            self.assertEqual(dirty_spans(old, new), [(0, 1, 2), (1, 2, 3)])
            self.assertEqual(cache.encode(new, not rgb), encode(new, not rgb))
            self.assertEqual(cache.encode(from_text("x")), encode(from_text("x")))
            cache.invalidate()
            self.assertEqual(cache.encode(from_text("x")), encode(from_text("x")))

    def test_exports_escape_and_validate(self):
        frame = from_text("<&>")
        self.assertIn("&lt;&amp;&gt;", to_html(frame))
        self.assertIn("&lt;", to_svg(frame))
        for text in ("\x1b[31m", "🙂", "\t"):
            with self.assertRaises(ValueError):
                from_text(text)

    def test_fragmented_keyboard_mouse_and_generic_keys(self):
        parser = Input()
        self.assertEqual(parser.feed(b"\x1b[119;", now=1), [])
        event = parser.feed(b"2:3u", now=1.01)[0]
        self.assertEqual(
            (event.key, event.shift, event.release, event.enhanced),
            ("w", True, True, True),
        )
        self.assertEqual(parser.feed(b"\x1b[A")[0].key, "up")
        self.assertEqual(parser.feed(b" ")[0].key, "space")
        self.assertEqual(parser.feed(b"\x1b[13u")[0].key, "enter")
        self.assertEqual(parser.feed(b"\x1b[<32;12;8M")[0].mouse, (12, 8))
        self.assertEqual(parser.feed(b"\x1b", now=2), [])
        self.assertEqual(parser.feed(now=2.1)[0].key, "exit")


class AssetTests(unittest.TestCase):
    def test_ppm_comments_blank_lines_and_validation(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from glyphforge._vendor.rendascii.resource import load_sprite

        with TemporaryDirectory() as folder:
            path = Path(folder) / "test.ppm"
            path.write_text("P3\n\n# demo\n2 1\n255\n255 0 0  0 255 0 # inline\n")
            self.assertEqual(
                load_sprite(path.name, folder + "/"), (["ff0000", "00ff00"],)
            )
            path.write_text("P3\n2 2\n255\n255 0 0\n")
            with self.assertRaises(ValueError):
                load_sprite(path.name, folder + "/")
