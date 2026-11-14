# RodAI Phase 5 Handover - Real-Video Tracking Slice

Date: 2026-11-14  
Status: **Prototype online tracking is wired into uploaded-video and browser-camera inference. It has not been evaluated on labeled footage and is not a production tracker.**

## Delivered

- Added a lightweight online association tracker that matches same-class detections using predicted overlap and center displacement, assigns session-local IDs, retains short gaps, and keeps a short image-space trail.
- Uploaded-video processing writes per-frame `tracks` alongside `detections` in `rodai.session.v1` JSONL records.
- Browser-camera inference writes and streams the same track records to the frontend.
- Video playback draws track IDs and recent trails. Completed uploads show session-level distinct track-ID count, peak simultaneous tracks in one processed frame, and class mix.
- Motion readouts use pixels per second only. No physical speed or distance is inferred without camera calibration.

## Interpretation and limits

The tracker is a practical baseline built on detector boxes. It is not a trained re-identification model; similar objects can swap IDs, missed detections can split one physical object into multiple IDs, and close objects can merge in association. Track IDs are unique only inside one session. Pixel trails and velocity help inspect movement but do not provide metres, km/h, collision prediction, or accident prevention.

The current DETR detector still processes every decoded upload frame. On CPU this may run slower than source playback. No throughput, latency, drop-rate or tracking-accuracy target has been measured. The browser-camera path is a local browser feed, not CCTV/RTSP ingestion.

## Acceptance still required

- Compare detector outputs to reviewed frame annotations and report precision/recall by class.
- Compare track identities to labeled sequences; report IDF1, ID switches, fragmentation, and representative failure clips.
- Check timestamp handling on variable-frame-rate and imperfect media; compare measured image-plane displacement against frame timestamps.
- Benchmark sustained processing on the verified development computer and owner-provided permissioned road footage.
- Keep absolute speed hidden until a per-camera ground-plane calibration and an error measurement are available.

Representative, permissioned footage is still needed for any claim about Kigali/Rwanda roads. The existing smoke clip only proves that inference and the session pipeline can run.

## Verification in this change

- Frontend TypeScript production build passed.
- Frontend ESLint passed.
- Backend Ruff was unavailable in the host environment; backend tests were not run. Run the backend CI workflow in the development environment before merging this branch.
