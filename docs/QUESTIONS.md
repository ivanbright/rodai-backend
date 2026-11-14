# Questions for the Owner — Phase 0 closeout

The consolidated owner response answers the former questions on target geography, camera sources, privacy defaults, commercial licensing preference, Python version, database, export priorities, frame transport, concurrency, UI direction, Railway topology, user access, upload limits, and hosted camera scope. See `DECISIONS.md` for the recorded requirements.

## Remaining confirmations / facts

1. **Phase 0 gate:** Review the completed report in `docs/handovers/phase-0.md`. Phase 0 remains pending until the owner sends the exact phrase `APPROVED: Phase 0`. The pasted decisions explicitly say they are not approval.
2. **Sample footage and permissions:** Provide or identify one or more legally usable sample videos representative of Kigali/Rwanda conditions. Include source, permission/licence, recording context, length, resolution/FPS, restrictions, and whether people/plates are identifiable. Do not download or copy unreviewed footage into the repository.
3. **Hardware:** The workspace confirms Python 3.13.2 on host and CPU-only PyTorch in Docker, but not host GPU status. From non-admin PowerShell, try `Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, CsProcessors, CsTotalPhysicalMemory` and `Get-PSDrive -Name C | Select-Object Used, Free`. For graphics details, run `dxdiag /t "$env:TEMP\rodai-dxdiag.txt"` and share the System and Display sections from that report. If a command is blocked, use Windows Settings > System > About and Task Manager > Performance > GPU; do not install GPU tooling or change drivers yet.
4. **Railway spending:** Select a Railway plan and explicit monthly spend ceiling before paid provisioning or deployment. Domain planning uses `rodai.cursorclick.dev`; do not configure DNS or purchase anything without separate approval.
5. **Privacy/legal implementation:** Confirm with qualified counsel or the relevant authority how Rwanda's personal-data law applies to the intended collection, processing, storage and sharing. The 7/30/7-day defaults are recorded but not implemented; confirm whether these defaults are acceptable for the first deployment.
6. **Phase 2 conformance:** The owner requirements for automatic retention and configurable camera capture controls must be reflected in an implementation/acceptance plan before Phase 3. Current code does not yet implement the retention windows or configurable 1280x720/JPEG quality controls. One-session enforcement is implemented through the session registry.

## Not blockers to architecture, but required before later work

- Detector source and weight licence review, class-map confirmation and commercial compatibility (before selecting/downloading weights).
- Design references/screenshots (before Phase 5 visual redesign).
- Performance targets after real Phase 3 benchmarks on representative footage and hardware.
