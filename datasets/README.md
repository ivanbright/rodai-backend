# Local benchmark video library

The library is disabled outside local development. Video files stay on this computer and are mounted read-only into the API container. RodAI does not download benchmark files for you.

## Add an authorized clip

1. Open the dataset's official source and terms links in the RodAI **Benchmark library**.
2. Download only footage you are permitted to use for this development and demonstration purpose. Do not use a clip for an investor presentation unless its terms allow that use.
3. Put the video under `datasets/<dataset-id>/clips/`. The default catalog contains `aicity-2021-track4`, `nexar-collision-prediction`, and `bdd100k`.
4. Add a clip entry to that dataset's `clips` array in `catalog.json`:

```json
{
  "id": "example-clip-01",
  "title": "Reviewed intersection clip",
  "file": "clips/example-clip-01.mp4",
  "rights_reviewed": true,
  "source_url": "https://official-source.example/dataset",
  "license_name": "Name of the applicable dataset license",
  "permitted_uses": "Local research and internal demonstration only",
  "privacy_reviewed": false,
  "event_type": "near_miss",
  "event_time_seconds": 12.4,
  "annotation_reference": "Official label file or manual-review note",
  "split": "evaluation"
}
```

`file` must be relative to the dataset folder. Supported formats are MP4, MOV, MKV, WebM, AVI, and M4V. Record the exact permitted uses for the copy you obtained; `rights_reviewed` must be true before RodAI will serve or analyze a clip. `privacy_reviewed` records whether the clip has been checked for faces/plates before any external sharing; it does not affect local analysis. Set `event_time_seconds` to `null` when there is no trusted event timestamp. Use event types such as `normal`, `near_miss`, `collision`, `stalled_vehicle`, or `unlabeled`; these are reference labels, not predictions from RodAI.

Only `catalog.json` and this guide are versioned. Video files and other dataset material remain ignored by Git. Keep the catalog's provenance and terms information accurate when adding clips.

## Start the local library

From the repository root, apply the database migration before starting the services, then start the local stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d rodai-db
docker compose -f docker-compose.yml -f docker-compose.local.yml run --build --rm rodai-api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

The API does not apply migrations on startup. The library is intentionally unavailable in staging and production.
