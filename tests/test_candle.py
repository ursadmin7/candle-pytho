import unittest
import candle


class TestCandle(unittest.TestCase):

    def test_version_exists(self):
        self.assertTrue(hasattr(candle, "VERSION"))

    def test_clamp_normal_value(self):
        self.assertEqual(candle.clamp(0.5), 0.5)

    def test_clamp_below_range(self):
        self.assertEqual(candle.clamp(-1), 0.0)

    def test_clamp_above_range(self):
        self.assertEqual(candle.clamp(2), 1.0)

    def test_smoothstep_midpoint(self):
        self.assertAlmostEqual(candle.smoothstep(0, 1, 0.5), 0.5)

    def test_rgb_escape(self):
        result = candle.rgb_escape(255, 128, 0)
        self.assertTrue(result.startswith("\033["))


if __name__ == "__main__":
    unittest.main()