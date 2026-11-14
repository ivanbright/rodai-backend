# Questions for the Owner — Phase 0 closeout

The consolidated owner response answers the former questions on target geography, camera sources, privacy defaults, commercial licensing preference, Python version, database, export priorities, frame transport, concurrency, UI direction, Railway topology, user access, upload limits, and hosted camera scope. See `DECISIONS.md` for the recorded requirements.

## Remaining confirmations / facts

1. **Phase 0 gate:** Review the completed report in `docs/handovers/phase-0.md`. Phase 0 remains pending until the owner sends the exact phrase `APPROVED: Phase 0`. The pasted decisions explicitly say they are not approval.
2. **Target-region footage:** No owner-provided sample collection is available. A CC0 Bangalore road-video smoke-test candidate and its limitations are documented in `docs/handovers/phase-0.md`; it is not Kigali footage and has not been downloaded or visually privacy-checked. A permissioned Kigali/Rwanda sample remains required for representative detector-quality acceptance. Do not use publicly accessible footage without checking its specific licence and permissions.
3. **Hardware:** Confirmed: Windows computer, Intel processor, 32 GB RAM. Still unknown: Windows edition/build, CPU model, GPU/VRAM, CUDA/driver and free disk. From non-admin PowerShell, try `Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, CsProcessors, CsTotalPhysicalMemory` and `Get-PSDrive -Name C | Select-Object Used, Free`. For graphics details, run `dxdiag /t "$env:TEMP\rodai-dxdiag.txt"` and share the System and Display sections. If blocked, use Windows Settings > System > About and Task Manager > Performance > GPU; do not install GPU tooling or change drivers.
4. **Railway spending:** Review the illustrative estimate in `docs/handovers/phase-0.md`; choose the plan and explicit monthly ceiling before paid provisioning/deployment. Domain is `rodai.cursorclick.dev`, DNS is Cloudflare; do not change DNS without separate approval.
5. **Privacy/legal:** The 7/30/7-day technical defaults are accepted, not legal compliance. Confirm with qualified counsel or the relevant authority how Rwanda's personal-data rules apply to collection, processing, storage and sharing, including identifiable people/plates, access requests, retention and deletion.
6. **Phase 2 closeout:** Automatic retention, configurable camera capture and the measurable tests/criteria are in the closeout plan in `docs/handovers/phase-0.md`. They remain unimplemented and must pass acceptance before Phase 3.

## Not blockers to architecture, but required before later work

- Detector source and weight licence review, class-map confirmation and commercial compatibility (before selecting/downloading weights).
- Design references/screenshots (before Phase 5 visual redesign).
- Performance targets after real Phase 3 benchmarks on representative footage and hardware.
