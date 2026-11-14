# RodAI Phase 6 Handover - Useful Video Results

Date: 2026-11-14  
Status: **Video-analysis experience updated to prioritize an annotated video and explain startup/stopped states. A 60-second local upload completed at 2 analyzed samples per second. Browser-rendered export still needs visual confirmation.**

## User workflow now

1. Select a road video and choose an analysis sampling rate. The local default is 2 model frames per second; 1 FPS is quicker, while 5 or 10 FPS takes longer on CPU and gives denser samples.
2. On first run, the detector may need to download or load its model. The UI explains this state. It shows the number of analyzed samples, not the total source frame count.
3. When results are ready, play the source preview with track boxes, IDs and trails aligned to analyzed timestamps. Review the observed track-ID counts and class mix.
4. Use **Save annotated video (.webm)** to render the browser-local source video and overlays into a downloadable video. For a stopped session, the export ends at its last analyzed timestamp.
5. Expand **Technical data for developers** only when frame-level JSONL is needed. It is machine-readable data for debugging or integrations, not the normal viewing result.

## Zero-frame stop diagnosis

For session `66375bc9-2fad-4057-8b1e-9e886ff80b0a`, the API reported 1,803 source frames and 0 analyzed frames. Its JSONL contained only a summary. API logs show a stop request while the pinned detector was still loading; no frame reached inference. The old UI nevertheless said partial results were available and exposed an empty JSONL download. The new UI reports that no analysis occurred, hides result/download actions when the analyzed count is zero, and labels the action **Cancel startup** until the first frame arrives.

## Sampling behavior

The upload API accepts `analysis_fps` from 1 to 15. Its configurable default is `RODAI_ANALYSIS_FPS=2`. Source frames are decoded in order; detector inference runs only when the next sample interval is reached. `processed_frames` now counts analyzed samples, and source frame indexes/timestamps remain in the JSONL records. This reduces unnecessary CPU inference for long 30 FPS footage, but low sampling may miss short-lived events. No performance or accident-detection claim follows from this change.

## Verification and remaining work

- TypeScript production build and frontend lint passed; backend Python compilation passed. No automated tests were run.
- The rebuilt Docker API and database are healthy. The user-uploaded 60.1-second, 1280 × 720, 30 FPS clip completed with 120 analyzed samples at 2 FPS; every analyzed sample contained detections. This is a pipeline smoke check, not an accuracy or representative-footage acceptance result.
- The upload path initially raised an unbound-local error while scheduling the background task. Fixed in commit `e52bb6d`; re-uploading the same local clip then completed successfully.
- Browser automation was unavailable in this environment. Open the completed recent session in the browser, confirm the video overlay, use **Save annotated video (.webm)**, and check the downloaded file's playback.
- Confirm audio preservation and codec compatibility in the target browser. If browser recording is unsupported, the app gives an error and keeps the annotated in-page preview available.
- Track IDs showed substantial fragmentation in this smoke clip; do not present track counts or identity stability as validated. The pinned detector/tracker still do not detect or predict accidents. Representative footage, labeled evaluation, hardware benchmarks, CCTV ingest, calibration, privacy review and incident logic remain future work.
