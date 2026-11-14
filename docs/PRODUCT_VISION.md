# RodAI Product Vision

Updated: 2026-11-14

## Product goal

RodAI is intended to turn real road-camera video into timely, reviewable road-safety information. The product direction is a fixed CCTV or road-camera feed that can detect and track road users, measure traffic movement, identify hazardous interactions, and show operators clear evidence and alerts. A future system may support prevention by giving people time to respond; the current prototype does not predict or prevent crashes.

The supplied screenshots are visual references for that destination. They are not proof of existing functionality, verified specifications, or instructions to copy all visible claims. Text inside the images (such as GPS update intervals, speeds, crash warnings, and signal control) is illustrative content, not owner-confirmed operating data.

## What the references suggest

- **Camera-first observation:** analyze actual footage from a fixed camera or dash camera, with detections drawn on the same video so people can inspect the result.
- **Road-user perception:** identify relevant vehicles, pedestrians, cyclists and other classes supported by the selected model, and keep identities stable across frames.
- **Movement and traffic measures:** estimate direction, speed, counts, flow and density. Absolute speed requires a camera-specific road-plane calibration or another trustworthy measurement source; pixels alone do not give metres per second.
- **Conflict and incident review:** flag observable events, explain the evidence and timestamps, and separate post-event incident detection from a prediction that a collision may occur.
- **Operator dashboard:** show camera/feed health, live or recent annotated video, counts and trends, and an alert queue with severity, time, camera and evidence clip.
- **Future integrations:** GPS/vehicle telemetry, signal status/control, multi-camera maps, and response workflows require compatible devices, data feeds, permissions and separate engineering. A CCTV stream by itself does not provide vehicle GPS or authorize signal control.

The top-down map, satellite/GPS overlays, vehicle-assistance displays, photorealistic scenes and dashboard graphics in the references show possible presentation styles or adjacent products. They are not grounds to claim that RodAI already has those sensors, feeds, analytics or integrations.

## Actual implementation today

- A pinned CPU DETR model detects a limited set of road-user objects in uploaded video and in the browser-camera path. Uploaded-video sampling is selectable; the local default is 2 analyzed frames per second to avoid needlessly running CPU inference on every source frame. The frontend displays tracked IDs and trails, summarizes observed track IDs, and can export the original footage with overlays as a browser-generated WebM. Raw JSONL remains available as developer data.
- A lightweight online tracker associates detections across nearby frames and estimates image-plane motion in pixels per second. It is a prototype association method; IDs can switch or split, and its pixel values are not calibrated vehicle speeds.
- For a completed uploaded-video session, an operator can draw a virtual line across the road view. RodAI reports the sampled tracked-ID crossings by direction and overlays the line during playback/export. This is an exploratory, session-local count based on sampled frames and unvalidated track identities; it is not a validated traffic count or physical speed measurement.
- One local smoke clip completed inference. This demonstrates that the pipeline runs; it does not demonstrate accuracy, reliable speed estimates, tracking quality, accident detection, collision prediction, CCTV streaming, or readiness for road deployment.
- A scripted SVG simulation workspace exists. It is a demonstration of deterministic rules and is **not** the product's real-video lab, validation evidence, or a substitute for camera footage. Do not count it as progress toward operational incident detection.
- The CCTV/RTSP ingest path, tracking validation, calibrated speed measurement, learned or validated conflict/incident logic, operator alert workflow, and representative Kigali/Rwanda evaluation are not yet implemented or accepted.

## Build sequence and acceptance evidence

Each stage should use real recorded or live camera video where specified, retain source provenance, and report what was actually measured.

1. **Reliable video foundation:** keep upload analysis usable, render and export the original video with model overlays, expose progress/errors, and provide readable results. Acceptance: supported-format fixtures process end to end, overlays align to sampled timestamps, and exported video plays with synchronized annotations.
2. **Road-user tracking:** improve and validate the prototype association tracker. Acceptance: evaluate detection precision/recall and tracking metrics such as IDF1 and ID switches on a reviewed, labeled, permissioned clip set; publish errors as well as successes. Do not call IDs stable until those results support the claim.
3. **Movement measurement:** the first slice now counts tracked-ID crossings and direction against an operator-drawn line on uploaded video. Next, persist line definitions as camera profiles and implement per-camera road-plane calibration before displaying physical speed or distance. Acceptance: compare counts and speed against manually reviewed ground truth from permissioned footage, report camera setup, sampling rate, identity fragmentation and uncertainty. The current line-count prototype does not meet that acceptance gate.
4. **CCTV ingestion and live operator view:** add a configurable, secured camera stream path (for example RTSP where the camera supports it), reconnect and health states, bounded queues, and dropped-frame reporting. Acceptance: sustained run on identified hardware with measured latency, throughput, CPU/RAM, frame drops and recovery behaviour.
5. **Conflict and incident alerts:** first implement transparent, auditable rules over tracked trajectories; distinguish collision/incident detection after an event from risk warnings before a possible event. Acceptance: evaluate against labeled positive and negative footage using warning lead time, missed events and false alerts per camera-hour. Do not call it prevention or predictive AI without evidence.
6. **Operator dashboard and privacy:** camera status, annotated evidence, alert review/history, role and access controls, retention, deletion audit and privacy treatment (including face/plate blur before sharing). Acceptance: user walkthrough and security/privacy review.
7. **Target-region evaluation and deployment decision:** use representative Rwanda/Kigali footage with documented permissions and hardware benchmarks. Set performance thresholds from those measurements; only then assess edge hardware, scaling, costs, hosting and any external integrations.

## Data and evaluation requirements

Real sample footage is required before representative video acceptance. For each clip, record source/owner, capture date and location context, permission and permitted uses, camera/viewpoint, resolution, frame rate, duration, weather/light conditions, whether an incident is present, annotation status, privacy review and any transformations. Keep private by default and do not download or commit unverified road footage.

Split clips by source/camera/time and scenario before training or tuning to reduce leakage. Maintain separate training, tuning and held-out evaluation sets. Report model and configuration versions, class definitions, calibration, sample counts, metrics, failure cases and limitations for every benchmark. Synthetic or scripted data may support software tests but cannot replace representative recorded footage in acceptance claims.

## Explicit non-claims

Until measured and reviewed, RodAI must not claim reliable accident prediction, accident prevention, real-time performance, production CCTV support, measured physical speeds, automatic smart-signal control, or validated Rwanda/Kigali performance. Alerts are decision support for a human operator, not emergency dispatch or enforcement instructions.
