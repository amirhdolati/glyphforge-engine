import importlib
import unittest
from examples.catalog import NAMES
from glyphforge.frame import validate


class GalleryTests(unittest.TestCase):
    def test_gallery_contract_determinism_and_animation(self):
        for name in NAMES[6:]:
            module = importlib.import_module("examples." + name)
            with self.subTest(example=name):
                for width, height in ((1, 1), (37, 13)):
                    frame = validate(module.frame(width, height, 1))
                    self.assertEqual((len(frame[0]), len(frame)), (width, height))
                    self.assertEqual(frame, validate(module.frame(width, height, 1)))
                self.assertNotEqual(
                    validate(module.frame(50, 20, 1)), validate(module.frame(50, 20, 3))
                )


class CameraTests(unittest.TestCase):
    def test_look_at_maps_eye_to_origin_and_target_to_forward(self):
        from glyphforge.mesh import look_at, matrix

        for eye in ((0, 0, -6), (4, 2, -6), (-3, 1, 4)):
            view = look_at(eye, (0, 0, 0))
            origin = matrix.transform_h(view, (*eye, 1))
            target = matrix.transform_h(view, (0, 0, 0, 1))
            for value in origin[:3]:
                self.assertAlmostEqual(value, 0)
            self.assertAlmostEqual(target[0], 0)
            self.assertAlmostEqual(target[1], 0)
            self.assertGreater(target[2], 0)

    def test_look_at_rejects_degenerate_poses(self):
        from glyphforge.mesh import look_at

        for eye, target, up in (
            ((0, 0, 0), (0, 0, 0), (0, 1, 0)),
            ((0, 0, 0), (0, 1, 0), (0, 1, 0)),
            ((0, 0, float("nan")), (0, 0, 0), (0, 1, 0)),
        ):
            with self.assertRaises(ValueError):
                look_at(eye, target, up)
