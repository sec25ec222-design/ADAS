import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adas.collision import Detection, estimate_distance_m, time_to_collision, classify  # noqa: E402
from adas.config import Config  # noqa: E402
from adas.fatigue import FatigueMonitor, eye_aspect_ratio  # noqa: E402
from adas.lane import detect_lane_lines, lane_offset, departure_warning  # noqa: E402
from adas.synthetic import make_frame  # noqa: E402


class TestCollision(unittest.TestCase):
    def setUp(self):
        self.cfg = Config()

    def test_distance_decreases_as_box_grows(self):
        near = estimate_distance_m(Detection(0, 0, 200, 100), self.cfg)
        far = estimate_distance_m(Detection(0, 0, 50, 25), self.cfg)
        self.assertLess(near, far)

    def test_ttc_none_when_not_closing(self):
        self.assertIsNone(time_to_collision(20.0, 20.0, 0.1))
        self.assertIsNone(time_to_collision(20.0, 25.0, 0.1))

    def test_ttc_value(self):
        # closes 1 m in 0.1 s => 10 m/s; 10 m away => TTC 1 s
        self.assertAlmostEqual(time_to_collision(11.0, 10.0, 0.1), 1.0, places=5)

    def test_classification(self):
        self.assertEqual(classify(None, self.cfg), "SAFE")
        self.assertEqual(classify(5.0, self.cfg), "SAFE")
        self.assertEqual(classify(2.0, self.cfg), "WARN")
        self.assertEqual(classify(1.0, self.cfg), "BRAKE")

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            estimate_distance_m(Detection(0, 0, 0, 10), self.cfg)
        with self.assertRaises(ValueError):
            time_to_collision(10, 9, 0)


class TestLane(unittest.TestCase):
    def setUp(self):
        self.cfg = Config()

    def test_centered_lane_is_ok(self):
        frame, _ = make_frame(drift=0)
        l, r = detect_lane_lines(frame)
        off = lane_offset(frame.shape, l, r)
        self.assertIsNotNone(off)
        self.assertEqual(departure_warning(off, self.cfg), "OK")

    def test_drift_triggers_warning(self):
        frame, _ = make_frame(drift=220)
        l, r = detect_lane_lines(frame)
        off = lane_offset(frame.shape, l, r)
        self.assertTrue(departure_warning(off, self.cfg).startswith("DEPARTING"))

    def test_no_lane_on_blank_frame(self):
        import numpy as np
        blank = np.zeros((540, 960, 3), dtype=np.uint8)
        l, r = detect_lane_lines(blank)
        self.assertEqual(departure_warning(lane_offset(blank.shape, l, r), self.cfg), "NO_LANE")


class TestFatigue(unittest.TestCase):
    def test_ear_open_vs_closed(self):
        open_eye = [(0, 0), (1, -1), (2, -1), (3, 0), (2, 1), (1, 1)]
        closed_eye = [(0, 0), (1, -0.1), (2, -0.1), (3, 0), (2, 0.1), (1, 0.1)]
        self.assertGreater(eye_aspect_ratio(open_eye), eye_aspect_ratio(closed_eye))

    def test_drowsy_after_sustained_closure(self):
        mon = FatigueMonitor(Config())
        state = "ALERT"
        for _ in range(20):  # 2 s of closed eyes at 10 Hz
            state = mon.update(0.1, 0.1)
        self.assertEqual(state, "DROWSY")

    def test_blink_does_not_trigger(self):
        mon = FatigueMonitor(Config())
        mon.update(0.1, 0.2)
        self.assertEqual(mon.update(0.3, 0.1), "ALERT")


if __name__ == "__main__":
    unittest.main()
