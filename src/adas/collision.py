"""Forward collision warning using pinhole-camera distance and time-to-collision (TTC)."""
from dataclasses import dataclass
from typing import Optional

from .config import Config


@dataclass
class Detection:
    x: int
    y: int
    w: int
    h: int


def estimate_distance_m(det: Detection, cfg: Config) -> float:
    """distance = (real_width * focal_length) / pixel_width"""
    if det.w <= 0:
        raise ValueError("Detection width must be positive")
    return cfg.vehicle_width_m * cfg.focal_length_px / det.w


def time_to_collision(dist_prev: float, dist_now: float, dt: float) -> Optional[float]:
    """TTC from two distance samples. None if the gap is not closing."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    closing_speed = (dist_prev - dist_now) / dt
    if closing_speed <= 0:
        return None
    return dist_now / closing_speed


def classify(ttc: Optional[float], cfg: Config) -> str:
    if ttc is None:
        return "SAFE"
    if ttc <= cfg.brake_ttc_s:
        return "BRAKE"
    if ttc <= cfg.warn_ttc_s:
        return "WARN"
    return "SAFE"
