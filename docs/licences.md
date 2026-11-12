# Licence inventory (Phase 1 candidates)

This is a preliminary inventory of selected Phase 1 packages; verify exact package metadata and include transitive dependencies/SBOM before release. No detector or model weight is selected.

| Component | Licence / note |
|---|---|
| Python | PSF license |
| FastAPI | MIT |
| Uvicorn | BSD-3-Clause |
| Pydantic / pydantic-settings | MIT |
| SQLAlchemy | MIT |
| Alembic | MIT |
| psycopg | LGPL-3.0-or-later (binary package bundles libpq; review distribution implications) |
| PyYAML | MIT |
| OpenCV headless Python package | Apache-2.0 |
| PyTorch / torchvision | BSD-3-Clause |
| React | MIT |
| Vite | MIT |
| TypeScript | Apache-2.0 |
| PostgreSQL | PostgreSQL License (permissive) |
| Ultralytics candidate | AGPL-3.0; separate Enterprise licence; network service may trigger source availability obligations. Not selected. |
| Original RT-DETR repository candidate | Apache-2.0 repository code; review every weight/checkpoint and upstream dependency separately. Not selected. |

No video/dataset/model artifacts are present, so their licences remain unreviewed. Public hosting is blocked on the owner's detector/licensing decision. Refer to [Ultralytics licensing](https://docs.ultralytics.com/) and the [original RT-DETR repository](https://github.com/lyuwenyu/RT-DETR); repository code licensing does not settle weight licensing.
