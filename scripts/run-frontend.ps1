$ErrorActionPreference = 'Stop'
$composeFiles = @('-f', 'docker-compose.yml', '-f', 'docker-compose.local.yml')
docker compose @composeFiles up -d rodai-db
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose @composeFiles run --build --rm rodai-api alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose @composeFiles up --build rodai-frontend rodai-api rodai-db
exit $LASTEXITCODE
