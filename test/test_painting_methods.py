import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from painting_methods import directional_brushstrokes


class PaintingMethodsTest(unittest.TestCase):
    def test_brush_pass_is_deterministic_and_keeps_base_canvas(self):
        base=Image.new('RGBA',(128,128),(20,30,40,255))
        marks=[([(12,64),(64,58),(116,64)],(245,120,95),10,.55)]
        first=directional_brushstrokes(base,marks,seed=21)
        second=directional_brushstrokes(base,marks,seed=21)
        self.assertEqual(first.size,base.size)
        self.assertEqual(first.tobytes(),second.tobytes())
        self.assertEqual(first.getpixel((2,2)),base.getpixel((2,2)))
        self.assertNotEqual(first.getpixel((64,60)),base.getpixel((64,60)))


    def test_natural_character_has_warm_skin_not_neon(self):
        from render_natural_character import render
        img = render()
        self.assertEqual(img.size, (900, 1200))
        cheek = img.getpixel((360, 480))
        hair = img.getpixel((450, 140))
        shirt = img.getpixel((450, 960))
        self.assertGreater(cheek[0], cheek[2])  # pele quente
        self.assertLess(hair[0] + hair[1] + hair[2], 280)  # cabelo escuro
        self.assertGreater(shirt[0] + shirt[1] + shirt[2], 420)  # linho claro
        self.assertLess(max(cheek), 250)  # sem bolha branca no rosto

    def test_misuki_construct_is_dark_study_not_neon(self):
        from render_misuki_construct import render
        img = render('front')
        self.assertEqual(img.size, (900, 1200))
        hair = img.getpixel((450, 220))
        paper = img.getpixel((40, 40))
        self.assertLess(sum(hair), 80)
        self.assertGreater(sum(paper), 600)

    def test_stroke_portrait_keeps_paper_and_a_face(self):
        from render_stroke_portrait import render
        img = render('misuki')
        self.assertEqual(img.size, (900, 1200))
        paper = img.getpixel((40, 40))
        cheek = img.getpixel((450, 560))
        self.assertGreater(sum(paper), 680)
        self.assertGreater(sum(cheek), 500)


if __name__=='__main__':
    unittest.main()
