# ADAS: Advanced Driver Assistance System (Prototype)

An affordable, camera-based driver assistance prototype that warns of lane drift, forward collisions and driver fatigue, aimed at cutting human-error road accidents.

## Problem
Most serious road crashes involve human error: distraction, fatigue, blind spots and slow reaction. Advanced safety systems are mostly limited to premium vehicles, so most cars on the road have no collision warning or lane assist.

## Solution
A low-cost sensing and decision pipeline that detects hazards in real time and alerts the driver (or flags a brake request) before a collision.

## Features
| Module | What it does | File |
|---|---|---|
| Forward Collision Warning | Estimates distance to the lead vehicle, computes time-to-collision (TTC), raises `WARN` / `BRAKE` | `src/adas/collision.py` |
| Lane Departure Warning | Canny + Hough lane detection, measures offset from lane centre | `src/adas/lane.py` |
| Fatigue Monitoring | Eye Aspect Ratio (EAR) logic, flags `DROWSY` after sustained eye closure | `src/adas/fatigue.py` |

## Architecture
```
[Sensors] -> [Perception] -> [Decision] -> [HMI alerts]
                                      \-> [Brake request]
```
Full details in `docs/technical-design.md`.

## Project structure
```
ADAS/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── docs/technical-design.md
├── src/adas/          # collision, lane, fatigue, demo
├── tests/             # unit tests
└── data/sample/       # sample demo video
```

## Quick start
```bash
git clone https://github.com/sec25ec222-design/ADAS.git
cd ADAS
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run the demo (generates a synthetic road video if none is given)
PYTHONPATH=src python -m adas.demo --out output.mp4
# Windows PowerShell:  $env:PYTHONPATH="src"; python -m adas.demo --out output.mp4
```

## Run the tests
```bash
python -m unittest discover -s tests -v
```

## Environment variables
| Variable | Default | Meaning |
|---|---|---|
| `ADAS_FOCAL_LENGTH_PX` | 700 | Camera focal length in pixels |
| `ADAS_VEHICLE_WIDTH_M` | 1.8 | Assumed real width of a car |
| `ADAS_WARN_TTC_S` | 2.5 | TTC below which a warning is raised |
| `ADAS_BRAKE_TTC_S` | 1.2 | TTC below which braking is flagged |
| `ADAS_LANE_OFFSET` | 0.25 | Lane offset that triggers a departure warning |
| `ADAS_EAR_THRESHOLD` | 0.21 | EAR below this means eyes closed |
| `ADAS_EAR_SECONDS` | 1.5 | Seconds of closure before a drowsiness alert |

## Current limitations
- The demo vehicle detector is a simple colour detector for the synthetic video; a trained detector (e.g. YOLO) is the next step.
- Distance uses a monocular pinhole model and needs camera calibration.
- The fatigue module has the EAR logic; a face-landmark model must supply the eye points.
- Research prototype, not a certified safety system.

## Roadmap
YOLO detection, radar/ultrasonic fusion, embedded deployment (Jetson / Raspberry Pi), driver HMI alerts.

## License
MIT, see `LICENSE`.
