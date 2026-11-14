$ErrorActionPreference = 'Stop'
docker compose run --rm rodai-api python -m pytest
docker compose run --rm rodai-frontend npm test
