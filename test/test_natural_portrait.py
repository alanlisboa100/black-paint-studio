import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from natural_portrait_engine import Painter, paint_eye, render_natural
from portrait_controls import PRESETS, normalize_options


class NaturalPortraitTests(unittest.TestCase):
    def test_soft_shading_stays_inside_mask(self):
        painter = Painter(128, 'economy')
        mask = painter.path_mask('M 300 300 L 600 300 L 600 600 L 300 600 Z')
        before = painter.im.copy()
        painter.soft((200, 200, 700, 700), (20, 10, 30), .8, 40, mask)
        difference = ImageChops.difference(before, painter.im).convert('L')
        self.assertIsNotNone(difference.getbbox())
        self.assertIsNone(ImageChops.multiply(difference, ImageChops.invert(mask)).getbbox())

    def test_seed_dimensions_and_real_checkpoints(self):
        card = json.loads((ROOT / 'misuki.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            first, report = render_natural(card, 128, 'economy', checkpoint_dir=folder)
            second, _ = render_natural(card, 128, 'economy')
            varied, _ = render_natural(card, 128, 'economy', seed=42)
            self.assertEqual(first.size, (128, 171))
            self.assertEqual(first.tobytes(), second.tobytes())
            self.assertNotEqual(first.tobytes(), varied.tobytes())
            stages = sorted(Path(folder).glob('*.png'))
            self.assertEqual(len(stages), 5)
            self.assertEqual(len({p.read_bytes() for p in stages}), 5)
            self.assertFalse(report['reference_pixels_used'])
            self.assertIsNone(report['semantic_fidelity_score'])

    def test_quality_and_invalid_inputs(self):
        self.assertEqual(Painter(720, 'economy').size, (720, 960))
        self.assertEqual(Painter(900, 'standard').size, (1800, 2400))
        for width in (0, 127, 1081, 1.5):
            with self.assertRaises(ValueError):
                Painter(width)
        with self.assertRaises(ValueError):
            Painter(128, 'unknown')
        with self.assertRaises(ValueError):
            render_natural({'palette': {'vermelhoIris': 'invalid'}}, 128)

    def test_iris_color_only_changes_eye_region(self):
        red, blue = Painter(450, 'economy'), Painter(450, 'economy')
        paint_eye(red, True, (139, 16, 24))
        paint_eye(blue, True, (16, 24, 139))
        bbox = ImageChops.difference(red.im, blue.im).getbbox()
        self.assertIsNotNone(bbox)
        self.assertGreaterEqual(bbox[0], 179)
        self.assertLessEqual(bbox[2], 201)
        self.assertGreaterEqual(bbox[1], 230)
        self.assertLessEqual(bbox[3], 254)

    def test_expression_presets_only_change_face_and_have_distinct_results(self):
        card = json.loads((ROOT / 'misuki.json').read_text())
        neutral, _ = render_natural(card, 300, 'economy')
        results = {neutral.tobytes()}
        for expression in PRESETS:
            image, report = render_natural(card, 300, 'economy', expression=expression)
            self.assertEqual(report['controls']['expression'], expression)
            self.assertEqual(image.size, neutral.size)
            results.add(image.tobytes())
            bbox = ImageChops.difference(neutral, image).getbbox()
            if bbox:
                self.assertGreaterEqual(bbox[0], 90)
                self.assertLessEqual(bbox[2], 215)
                self.assertGreaterEqual(bbox[1], 130)
                self.assertLessEqual(bbox[3], 240)
        self.assertEqual(len(results), len(PRESETS))

    def test_control_validation_and_explicit_overrides(self):
        config = normalize_options({'expression':'sad','eye_open':1.1}, expression='happy')
        self.assertEqual(config['eye_open'], 1.1)
        self.assertEqual(config['mouth_curve'], .85)
        for options in [{'eye_open':True},{'eye_open':float('nan')},{'gaze_x':float('inf')},
                        {'mouth_open':2},{'eye_width':'wide'},{'new_feature':1},
                        {'cloth_material':'leather'},{'expression':'unknown'}]:
            with self.assertRaises(ValueError):normalize_options(options)

    def test_extreme_eye_controls_keep_iris_in_transformed_eye(self):
        first, second = Painter(300, 'economy'), Painter(300, 'economy')
        options={'eye_open':.5,'eye_width':.8,'eye_tilt':.6,'gaze_x':1,'gaze_y':1,'iris_size':1.15}
        first.options=second.options=normalize_options(options)
        paint_eye(first,True,(139,16,24));paint_eye(second,True,(16,24,139))
        bbox=ImageChops.difference(first.im,second.im).getbbox()
        self.assertIsNotNone(bbox)
        self.assertGreaterEqual(bbox[0],115);self.assertLessEqual(bbox[2],140)
        self.assertGreaterEqual(bbox[1],151);self.assertLessEqual(bbox[3],172)

    def test_fabric_material_does_not_repaint_the_face(self):
        card=json.loads((ROOT/'misuki.json').read_text())
        velvet,_=render_natural(card,300,'economy',options={'cloth_material':'velvet'})
        satin,_=render_natural(card,300,'economy',options={'cloth_material':'satin'})
        bbox=ImageChops.difference(velvet,satin).getbbox()
        self.assertIsNotNone(bbox)
        self.assertGreaterEqual(bbox[1],266)
