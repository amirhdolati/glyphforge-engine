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
