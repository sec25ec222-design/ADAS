"""Lane detection and departure warning (Canny + Hough transform)."""
from typing import Optional, Tuple

import cv2
import numpy as np

from .config import Config


def _roi_mask(edges: np.ndarray) -> np.ndarray:
    h, w = edges.shape
    mask = np.zeros_like(edges)
    poly = np.array([[(0, h), (int(w * 0.2), int(h * 0.6)),
                      (int(w * 0.8), int(h * 0.6)), (w, h)]], dtype=np.int32)
    cv2.fillPoly(mask, poly, 255)
    return cv2.bitwise_and(edges, mask)


def detect_lane_lines(frame: np.ndarray) -> Tuple[Optional[tuple], Optional[tuple]]:
    """Return (left_line, right_line) as (slope, intercept), or None if not found."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = _roi_mask(cv2.Canny(blur, 50, 150))
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40, minLineLength=40, maxLineGap=100)
    left, right = [], []
    if lines is None:
        return None, None
    for x1, y1, x2, y2 in lines[:, 0]:
        if x2 == x1:
            continue
        slope = (y2 - y1) / (x2 - x1)
        if abs(slope) < 0.4:  # ignore near-horizontal lines
            continue
        intercept = y1 - slope * x1
        (left if slope < 0 else right).append((slope, intercept))
    l = tuple(np.mean(left, axis=0)) if left else None
    r = tuple(np.mean(right, axis=0)) if right else None
    return l, r


def lane_offset(frame_shape, left, right) -> Optional[float]:
    """Vehicle offset from lane centre, as a fraction of lane width.
    Negative = drifting left, positive = drifting right."""
    if left is None or right is None:
        return None
    h, w = frame_shape[:2]
    y = h  # evaluate at bottom of the image
    xl = (y - left[1]) / left[0]
    xr = (y - right[1]) / right[0]
    lane_w = xr - xl
    if lane_w <= 0:
        return None
    centre = (xl + xr) / 2
    return (w / 2 - centre) / lane_w


def departure_warning(offset: Optional[float], cfg: Config) -> str:
    if offset is None:
        return "NO_LANE"
    if abs(offset) > cfg.lane_offset_threshold:
        return "DEPARTING_LEFT" if offset < 0 else "DEPARTING_RIGHT"
    return "OK"
