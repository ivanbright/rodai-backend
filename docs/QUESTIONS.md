# Questions for the Owner — Phase 0 (updated for Docker/Railway addendum)

Please answer in one consolidated reply. Items marked **blocks a concrete design or later phase** need a decision before that work starts.

1. **Deployment context (blocks target design/evaluation):** Where will RodAI first be demonstrated or used? Is Kigali/Rwanda road footage the target? Which data-protection rules apply to that footage?
2. **Camera and footage (blocks motion/risk design and sample-video acceptance):** Is the intended source fixed roadside/CCTV, dashcam, drone, phone, or another camera? Do you have sample videos? For each, provide source, licence/permission, duration, resolution/FPS, recording context, and any restrictions. May samples be copied into `datasets/raw/samples/`?
3. **Privacy (blocks upload/export behavior):** Should uploaded footage be deleted after processing? How long should session results persist? May exports contain frames or annotated video? Is face/plate blurring required?
4. **Licensing (blocks detector/weights selection):** Is RodAI strictly research/open-source under compatible terms, or might it be distributed commercially/proprietarily? Is AGPL-3.0 acceptable, or should we restrict candidates to permissively licensed code and separately reviewed weights?
5. **Hardware (blocks workload/performance and install plan):** Please provide Windows edition, CPU, RAM, GPU and VRAM, CUDA/driver availability, and free disk space. `systeminfo` and CIM queries were denied in this environment; `nvidia-smi` is unavailable.
6. **Python compatibility:** Can we use a Python 3.12 project environment alongside installed Python 3.13.2? Current PyTorch Windows instructions list Python 3.9–3.12.
7. **Session persistence and export:** Are file-based JSONL results sufficient, or is SQLite/searchable history across restarts required? Should annotated video export be included in v0.1?
8. **Transport proposal:** Approve binary WebSocket JPEG frames with client capture timestamps and frame IDs, and ordered processing for uploaded videos versus bounded newest-frame-wins live preview with counted drops? Any capture-resolution/quality cap requirement?
9. **Concurrency:** Is one simultaneous session acceptable for v0.1? What should happen when another session is started?
10. **Design references:** Please supply screenshots or a design reference before Phase 5. None are present in the repository.
11. **Phase 0 gate:** After reviewing this report and the decisions above, do you approve Phase 0? The required gate phrase is `APPROVED: Phase 0`.

## Addendum decisions required

12. **Railway domain:** What domain/subdomain and DNS provider should be used? Do not share credentials; those belong in Railway's secret settings.
13. **Railway budget/plan:** Which Railway plan and monthly spend ceiling should the design target? Current plan resource ceilings vary substantially; set workspace usage limits as part of deployment.
14. **Users:** Is deployed access for only you, invited testers, or the public? This sets account creation, rate limits and upload quotas.
15. **Frontend topology:** Accept one Railway app service serving backend and built frontend from the same origin, or do you require a separate frontend service/CDN?
16. **Local database:** Accept PostgreSQL in Docker Compose to match production, or choose SQLite locally and accept database behavior drift?
17. **Uploads:** What maximum upload size and duration should be configured? What retention period applies to uploads, exports and model files?
18. **Public camera:** Must browser-camera processing be supported on the public deployment, or is uploaded-video processing sufficient for first release? Public live video consumes user bandwidth and service CPU.
19. **Authentication:** Unless you direct otherwise, the proposed first design is owner-managed/invite-only accounts with password hashes and secure session cookies; confirm audience and whether account self-registration is prohibited.

Existing questions 1–10 remain open, especially camera/footage, data permissions, privacy regime, detector license, hardware facts, Python 3.12, and sample videos.
