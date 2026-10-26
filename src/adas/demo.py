"""Run the ADAS pipeline on a video.
Usage (from repo root): PYTHONPATH=src python -m adas.demo [--video path] [--out out.mp4]"""
import argparse
import os

import cv2

from .collision import Detection, estimate_distance_m, time_to_collision, classify
from .config import Config
from .lane import detect_lane_lines, lane_offset, departure_warning
from .synthetic import write_demo_video


def find_lead_vehicle(frame):
    """Simple colour-based detector for the synthetic demo (red car).
    Replace with a real detector (e.g. YOLO) for road footage."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 120, 80), (10, 255, 255))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    return Detection(x, y, w, h) if w > 10 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="data/sample/demo.mp4")
    ap.add_argument("--out", default="output.mp4")
    args = ap.parse_args()
    cfg = Config()

    if not os.path.exists(args.video):
        os.makedirs(os.path.dirname(args.video) or ".", exist_ok=True)
        write_demo_video(args.video)
        print(f"Generated synthetic demo video at {args.video}")

    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w, h = int(cap.get(3)), int(cap.get(4))
    out = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    prev_dist, alerts = None, {"WARN": 0, "BRAKE": 0, "DEPARTING": 0}

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        left, right = detect_lane_lines(frame)
        lane_state = departure_warning(lane_offset(frame.shape, left, right), cfg)
        det = find_lead_vehicle(frame)
        fcw = "SAFE"
        if det:
            dist = estimate_distance_m(det, cfg)
            if prev_dist is not None:
                fcw = classify(time_to_collision(prev_dist, dist, 1 / fps), cfg)
            prev_dist = dist
            cv2.rectangle(frame, (det.x, det.y), (det.x + det.w, det.y + det.h), (0, 255, 0), 2)
            cv2.putText(frame, f"{dist:.1f} m", (det.x, det.y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        if fcw in alerts:
            alerts[fcw] += 1
        if lane_state.startswith("DEPARTING"):
            alerts["DEPARTING"] += 1
        color = (0, 0, 255) if fcw == "BRAKE" else (0, 165, 255) if fcw == "WARN" else (0, 200, 0)
        cv2.putText(frame, f"FCW: {fcw}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"LANE: {lane_state}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 165, 255) if lane_state.startswith("DEPARTING") else (0, 200, 0), 2)
        out.write(frame)

    cap.release()
    out.release()
    print(f"Done. Output: {args.out}")
    print(f"Frames with alerts: {alerts}")


if __name__ == "__main__":
    main()
