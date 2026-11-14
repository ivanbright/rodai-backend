# Privacy and data handling

## Owner requirements

Road footage may identify people and vehicles. The owner targets selected-user research and demonstrations in Rwanda, especially Kigali footage, and requires privacy controls to be designed in from the start. The owner-provided defaults are:

- Uploaded originals: retain for up to 7 days, configurable.
- Session metadata and processing results: up to 30 days, configurable.
- Exported files: up to 7 days, configurable.
- Model files/checkpoints: retain until manually deleted.
- Private by default; deletion of uploads and associated results must be available.
- Do not include original frames in result exports by default.
- Face/registration-plate blur is required before footage is shared externally. Do not call footage anonymized unless the blur was applied and checked.

These are product requirements, not a legal conclusion. The applicable requirements under Rwanda's personal-data and privacy law for the specific collection, processing and sharing scenario need qualified review. Record provenance and permissions for each dataset/video. Do not collect, store, share or publish footage without permission.

## Current implementation state

The local Phase 2 pipeline writes upload bytes temporarily, deletes the source after processing, and stores results until the session is manually deleted. Automated 7-day upload/export and 30-day result expiry is not implemented. Current behavior is more aggressive for source video than the proposed default and less bounded for result retention; make both configurable before a hosted release. Browser-camera frame data is processed in-session and is not exported as source frames.

Do not expose the service publicly until authentication, authorization, origin checks, upload quotas, retention, deletion, privacy notice and backup/deletion behavior are implemented and reviewed. Keep all video and results private by default. Avoid raw frame content in JSONL.
