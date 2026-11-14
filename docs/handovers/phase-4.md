# RodAI Phase 4 Handover - Controlled Road Safety Lab

Date: 2026-11-14  
Status: **First interactive simulation slice implemented. This is a scripted scenario demonstration, not a learned or validated crash-prediction system.**

## Available in the demo

Open `http://localhost:5173` and choose **Simulation lab**. The lab currently contains three controlled cases:

1. Sudden braking / rear-end conflict.
2. Pedestrian entering a marked crossing.
3. Two vehicles approaching an intersection conflict zone.

Each scene advances in real time. It displays agent IDs and boxes, a time-to-conflict countdown, a rule-based risk indicator, and an optional simulated braking response. Turn braking off to let the scripted scenario reach its impact point. Reset or select another scenario to replay. **Video analysis** remains available as a separate workspace.

## How to interpret it

The current scenarios are deterministic scripts with known paths and event times. The displayed risk value is a demonstrator score derived from the scenario countdown; it is not calibrated probability. Agents are rendered from scenario state, so no camera detector, tracker, learned motion model, or accident-prediction model is being evaluated here. The “impact avoided” result means the scripted braking rule changed the simulated agent path before the scripted conflict point. It does not demonstrate prevention in real traffic.

## Test-library direction

The next increment should turn the three hand-authored scenes into a versioned scenario library. Each case should define road geometry, camera view, actor identities and classes, timestamped ground-truth trajectories, conflict zones, event timing, expected alerts, and expected outcomes. Use fixed random seeds for repeatable runs and record scenario/version, model/version, configuration, output events and metrics per run.

Proposed scenario families: following-distance and sudden braking; pedestrian and cyclist crossings; uncontrolled and signalized intersections; turning conflicts; low-light, rain, occlusion and camera-placement variants; and safe non-conflict controls to measure false alarms. Synthetic variants must be marked synthetic and kept distinct from permissioned recorded footage.

## Planned model and evaluation path

1. Generate or author repeatable scenes with complete ground truth.
2. Render camera-like frames that do not reveal hidden labels to the perception pipeline.
3. Feed image detections into tracking, estimate paths and speed, then calculate conflict warnings from the observed paths.
4. Evaluate detections, track continuity, warning lead time, missed conflicts, false alerts per simulated hour, and intervention outcomes against ground truth.
5. Keep train, tune and held-out scenario families separate; do not report training-scene results as independent validation.
6. Later compare model or policy versions against the same library and publish run-level evidence.

Scenario labels provide supervised examples; the model does not automatically train itself merely by watching scenarios. Any training set, weights and data sources need provenance/licence review before selection and use. Target-region acceptance still requires representative Rwanda/Kigali footage with documented rights.

## Current scope and next acceptance gates

- Delivered: three selectable animated scenes, deterministic countdown, conflict warning, simulated braking toggle, impact/avoidance outcome, clear synthetic/rule-based disclosure, and a separate video-analysis tab.
- Remaining for a richer lab: configurable scene builder, versioned scenario manifests, scenario persistence/run history, frame and ground-truth export, varied camera/weather/lighting/occlusion rendering, realistic agent dynamics, and evaluation dashboards.
- Remaining perception work: connect rendered frames to the actual detector; tracking with stable IDs; trajectory estimation; event logic based on observed model output rather than hidden ground truth; reviewed alert thresholds; and measured false-positive/false-negative behavior.
- A simulation result is not evidence of real-world accuracy. Benchmarks still require actual hardware and representative permissioned footage. No operational deployment or accident-prevention claim is authorized by this prototype.

## Verification

`npm run build` passed after the simulation workspace was added. Screenshot verification was unavailable because the browser-control service could not connect in this session; confirm the rendered layout at the local demo URL during interactive review.
