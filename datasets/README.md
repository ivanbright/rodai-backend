# Local road video library

The library is disabled outside local development. Video files stay on this computer and are mounted read-only into the API container. The two open-road demos are downloaded by `scripts/download-open-road-demos.ps1`; the files are ignored by Git and are not included in container images.

## Included local demo footage

| Clip | Source and creator statement | Intended use | Limit |
| --- | --- | --- | --- |
| Rainy road approach (15.3 s, 1280x720 transcode) | [Wikimedia Commons source page](https://commons.wikimedia.org/wiki/File:Dest-20220814_170517.ogv), uploader states own work and declares CC0 1.0 | Local road-scene perception workflow | The short excerpt does not contain a verified collision label or event time. It is not an accident example. |
| Berlin motorway at night (11.2 s, 1920x1080) | [Wikimedia Commons source page](https://commons.wikimedia.org/wiki/File:Berlin_Bundesautobahn_100_2026-03-25_mov03.webm), uploader states own work and declares CC0 1.0 | Local road-scene perception workflow | Unlabeled night traffic, not an incident or target-region evaluation set. |

Both catalog entries mark privacy review pending. Keep clips local and private until faces and registration plates have been reviewed or obscured before sharing. The CC0 notices address copyright as declared by the uploaders; they do not clear privacy, publicity, or other applicable rights. Neither clip represents Kigali/Rwanda road conditions.

SHA-256 checksums of the local files are pinned in the download script so re-downloads can be verified.

## Add another authorized clip

1. Open the source and usage terms for the video.
2. Download only footage permitted for the intended development and demonstration use. Do not use a clip in an investor presentation unless its terms allow that use and privacy has been reviewed.
3. Put the video under `datasets/<dataset-id>/`.
4. Add a clip entry to that dataset's `clips` array in `catalog.json`:

```json
{
  "id": "example-clip-01",
  "title": "Reviewed intersection clip",
  "file": "example-clip-01.mp4",
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

`file` is relative to the dataset folder. Supported formats are MP4, MOV, MKV, WebM, AVI, and M4V. `rights_reviewed` is an operator checklist gate, not proof of legal permission. Keep `event_time_seconds` null unless a trusted annotation or manual review supplies a timestamp. Event types are reference labels, never RodAI predictions.

Only `catalog.json` and this guide are versioned. Video files and other dataset material remain ignored by Git. Keep source, terms and privacy status accurate when registering clips.

## Start the local library

From the repository root, apply the database migration before starting the services, then start the local stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d rodai-db
docker compose -f docker-compose.yml -f docker-compose.local.yml run --build --rm rodai-api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

The API does not apply migrations on startup. The library is intentionally unavailable in staging and production.
