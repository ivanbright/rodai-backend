# Privacy and data handling

Road footage may identify people and vehicles. No production storage or retention behavior is implemented yet. The current foundation creates a configured local data directory and reports free/total space; it does not accept or store video.

Before video ingestion/public deployment, the owner must choose the applicable data-protection rules, footage permissions, upload and export retention periods, delete-my-data behavior, whether frame/video exports are allowed, and whether plate/face blurring is needed. By default, no raw frames should be embedded in JSONL exports. Do not treat this note as legal advice.

Future uploaded content must be validated, assigned randomized storage names beneath the configured data directory, never executed, and stored only on the persistent volume when deployed. Implement configurable retention and deletion only after owner decisions are recorded.
