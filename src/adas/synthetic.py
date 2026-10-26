"""Generate a synthetic road video so the demo runs without any external data."""
import cv2
import numpy as np


def make_frame(w=960, h=540, drift=0.0, car_width=60):
    """drift: horizontal shift of the lane (px) simulating the car drifting.
    car_width: lead-car width in px (grows as the car gets closer)."""
    img = np.full((h, w, 3), (60, 60, 60), np.uint8)
    cv2.rectangle(img, (0, 0), (w, int(h * 0.55)), (200, 180, 140), -1)  # sky
    cx = int(w / 2 + drift)
    horizon = int(h * 0.6)
    cv2.line(img, (cx - 40, horizon), (cx - 380, h), (255, 255, 255), 8)
    cv2.line(img, (cx + 40, horizon), (cx + 380, h), (255, 255, 255), 8)
    cw = int(car_width)
    ch = int(cw * 0.8)
    x = cx - cw // 2
    y = horizon + 10
    cv2.rectangle(img, (x, y), (x + cw, y + ch), (30, 30, 200), -1)  # lead car (red)
    return img, (x, y, cw, ch)


def write_demo_video(path="data/sample/demo.mp4", frames=90, fps=30):
    w, h = 960, 540
    out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for i in range(frames):
        drift = 220 * np.sin(i / frames * np.pi)           # drifts right then back
        car_w = 60 + i * 2.2                                # lead car grows = approaching
        frame, _ = make_frame(w, h, drift, car_w)
        out.write(frame)
    out.release()
    return path
