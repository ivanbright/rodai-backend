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

No video or dataset clips are bundled in the repository, and no model-weight choice is changed by the benchmark library. The local catalog points to these candidate data sources; its entries are not permission to use their media. Review the specific agreement for the exact file and intended use before setting `rights_reviewed` to `true`, and get permission for any external investor presentation if the terms are unclear.

| Dataset source | Intended MVP use | Rights / limits to check |
|---|---|---|
| [AI City Challenge 2021 Track 4](https://www.aicitychallenge.org/ai-city-challenge-dataset-access/) | Fixed-camera traffic anomaly inputs | Challenge page lists Track 4 for access; the FAQ describes a dataset participation agreement. Check its current access terms. |
| [Nexar Collision Prediction](https://huggingface.co/datasets/nexar-ai/nexar_collision_prediction) | Dashcam near-miss/collision timing | Nexar Open Data License requires attribution and restricts resale, redistribution for profit, and re-identification. |
| [BDD100K](https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst) | General road-user / scene perception | The dataset download terms are separate from the toolkit license; review the data license before downloading or using it. |

The benchmark catalog keeps clip paths and terms metadata outside the image and repository. Its `rights_reviewed` field is an operator checklist gate, not legal review or proof of permission. Public hosting is blocked on the owner's detector/licensing decision. Refer to [Ultralytics licensing](https://docs.ultralytics.com/) and the [original RT-DETR repository](https://github.com/lyuwenyu/RT-DETR); repository code licensing does not settle weight licensing.
