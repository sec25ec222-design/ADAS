import os
from dataclasses import dataclass


def _f(name, default):
    return float(os.getenv(name, default))


@dataclass
class Config:
    # Forward collision warning
    focal_length_px: float = _f("ADAS_FOCAL_LENGTH_PX", 700.0)
    vehicle_width_m: float = _f("ADAS_VEHICLE_WIDTH_M", 1.8)
    warn_ttc_s: float = _f("ADAS_WARN_TTC_S", 2.5)
    brake_ttc_s: float = _f("ADAS_BRAKE_TTC_S", 1.2)
    # Lane departure warning
    lane_offset_threshold: float = _f("ADAS_LANE_OFFSET", 0.25)
    # Fatigue monitoring
    ear_threshold: float = _f("ADAS_EAR_THRESHOLD", 0.21)
    ear_closed_seconds: float = _f("ADAS_EAR_SECONDS", 1.5)
