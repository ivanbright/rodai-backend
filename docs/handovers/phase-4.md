# RodAI Phase 4 Handover - Scripted Demonstration (Not the Product Lab)

Date: 2026-11-14  
Status: **A small scripted UI demonstration exists. Owner-provided visual references clarified that the intended lab must analyze real road video; this scripted work does not satisfy that goal and must not be represented as the core lab.**

The real-video product direction and acceptance sequence now live in [PRODUCT_VISION.md](../PRODUCT_VISION.md). The screenshots supplied on 2026-11-14 are references, not evidence that their displayed analytics, sensors or integrations exist in RodAI.

## Available in the demo

Open `http://localhost:5173` and choose **Simulation lab**. The lab currently contains three controlled cases:

1. Sudden braking / rear-end conflict.
2. Pedestrian entering a marked crossing.
3. Two vehicles approaching an intersection conflict zone.

Each scene advances in real time. It displays scripted agent IDs and boxes, a time-to-conflict countdown, a rule-based risk index, and an optional simulated braking response. Turn braking off to let the scripted scenario reach its impact point. Reset or select another scenario to replay. **Video analysis** remains available as a separate workspace.

The optional **Run detector on these frames** control rasterizes the current SVG scene and streams it to the existing live DETR endpoint. Returned DETR boxes are overlaid in a separate color; frame and detected-object counts are displayed. This inference path is implemented, but the live synthetic-frame WebSocket flow was not end-to-end verified in this session.

## How to interpret it

The current scenarios are deterministic scripts with known paths and event times. The displayed risk index is a demonstrator score derived from the scenario countdown; it is not calibrated probability. Optional DETR detections are real model outputs on simple, hand-drawn vector frames, but they do not feed the risk index or braking rule. The lab has no tracker or learned motion model. The “simulated conflict avoided” result means the scripted braking rule changed the simulated agent path before the scripted conflict point. It does not demonstrate prevention in real traffic.

## Scenario manifest

The first versioned manifest is `frontend/src/scenarios/road-conflicts.v1.json` (`rodai.scenario-library.v1`, library version `1.0.0`). It records three cases, scene layout, coordinate space and update rate, scripted actor identities/classes/roles/paths, time-to-conflict, conflict point, and expected outcomes with/without the simulated response. The UI renders each manifest scene and can pass those rendered frames through DETR. This is a small, hand-authored test bank; it has no randomized variants, photorealistic rendered camera frames, or persistent run records yet.

Earlier planning proposed additional scripted variants. That proposal is superseded as the next product step by the real-video roadmap in `PRODUCT_VISION.md`. Keep this demonstration isolated and clearly labeled if it remains in the UI; do not present additional scripted variants as progress toward the camera product.

## Earlier synthetic-data proposal (not the current product path)

Synthetic scenarios can support repeatable software checks and may complement model development, but they are not the requested real-video lab and cannot establish performance on CCTV footage. Refer to `PRODUCT_VISION.md` for the active sequence and real-footage acceptance evidence.

The model does not automatically train itself by watching video. Training data, weights and sources require provenance/licence review before selection and use. Target-region acceptance requires representative Rwanda/Kigali footage with documented rights.

## Current scope and limits

- Delivered: three selectable animated scenes, a versioned scenario manifest, deterministic countdown, conflict warning, simulated braking toggle, optional live DETR inference on rendered frames with a separate detection overlay, impact/avoidance outcome, clear synthetic/rule-based disclosure, and a separate video-analysis tab.
- This scripted simulation is not a required product milestone and should not be expanded as a substitute for real-video capabilities.
- The relevant next work is real-video tracking, calibrated movement measurement, CCTV ingestion, auditable incident/conflict analysis, and evaluation against labeled, permissioned footage as specified in [PRODUCT_VISION.md](../PRODUCT_VISION.md).
- A simulation result is not evidence of real-world accuracy. Benchmarks still require actual hardware and representative permissioned footage. No operational deployment or accident-prevention claim is supported by this prototype.

## Verification

`npm run build` and `npm run lint` passed after the simulation workspace and optional detector stream were added. The local Vite page and transformed simulation module return HTTP 200. Screenshot verification and the live synthetic-frame WebSocket flow were unavailable because the browser-control service could not connect in this session; verify them during interactive review.
