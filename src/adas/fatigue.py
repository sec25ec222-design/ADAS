"""Driver fatigue detection from the Eye Aspect Ratio (EAR).
Landmarks come from any face-landmark model (e.g. MediaPipe); this module holds only the logic."""
import math
from typing import Sequence, Tuple

from .config import Config

Point = Tuple[float, float]


def _d(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def eye_aspect_ratio(eye: Sequence[Point]) -> float:
    """eye = 6 landmarks p1..p6. EAR = (|p2-p6| + |p3-p5|) / (2|p1-p4|)"""
    if len(eye) != 6:
        raise ValueError("Expected 6 eye landmarks")
    p1, p2, p3, p4, p5, p6 = eye
    return (_d(p2, p6) + _d(p3, p5)) / (2.0 * _d(p1, p4))


class FatigueMonitor:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.closed_for = 0.0

    def update(self, ear: float, dt: float) -> str:
        if ear < self.cfg.ear_threshold:
            self.closed_for += dt
        else:
            self.closed_for = 0.0
        return "DROWSY" if self.closed_for >= self.cfg.ear_closed_seconds else "ALERT"
