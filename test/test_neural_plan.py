import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from render_neural_plan import render_plan, to_abs, bezier_samples

class NeuralPlanTests(unittest.TestCase):
    def test_arc_samples_are_preserved(self):
        commands=to_abs('M 100 100 A 50 50 0 0 1 200 100')
        self.assertGreater(len(bezier_samples(*commands[1],(100,100))),5)
    def test_smooth_curve_resets_after_line(self):
        commands=to_abs('M 0 0 C 10 10 20 20 30 30 L 40 40 S 50 50 60 60')
        self.assertEqual(commands[-1][1][0],(40,40))
    def test_partial_command_and_nonfinite_rejected(self):
        with self.assertRaises(ValueError): to_abs('M 0 0 C 1 2')
        with self.assertRaises(ValueError): to_abs('M 1e999 0 L 5 5')
    def test_zero_opacity_and_resolution_limit(self):
        plan={'background':'#ffffff','viewBoxHeight':1000,'elements':[{'path':'M 0 0 L 1000 0 L 1000 1000 L 0 1000 Z','fill':'#ff0000','stroke':'none','opacity':0}]}
        image,stats=render_plan(plan,128)
        self.assertEqual(image.getpixel((64,64)),(255,255,255))
        with self.assertRaises(ValueError):render_plan(plan,8192)

class MisukiIdentityTests(unittest.TestCase):
    def test_card_colors_and_visual_checkpoints(self):
        import tempfile
        from render_misuki_portrait import build_plan
        plan=build_plan()
        self.assertEqual(plan['elements'][63]['fill'],'#8B1018')
        self.assertEqual(plan['elements'][65]['fill'],'#C41E3A')
        with tempfile.TemporaryDirectory() as folder:
            image,stats=render_plan(plan,300,folder)
            self.assertEqual(stats['skip'],0)
            self.assertEqual(len(list(Path(folder).glob('etapa_*.png'))),5)
            self.assertGreater(image.height,300)
