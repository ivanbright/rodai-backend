$ErrorActionPreference = 'Stop'
docker compose run --rm backend python -m pytest
docker compose run --rm frontend npm test
