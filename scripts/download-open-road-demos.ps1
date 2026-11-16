$ErrorActionPreference = 'Stop'

$items = @(
    @{
        Name = 'rainy-road-context.webm'
        Url = 'https://upload.wikimedia.org/wikipedia/commons/transcoded/6/6a/Dest-20220814_170517.ogv/Dest-20220814_170517.ogv.720p.vp9.webm'
        Sha256 = 'CBB505AD629A43BDEC3D01010036B108C8235E9FBB29F5B979B690C7D5D0B6F8'
    },
    @{
        Name = 'berlin-night-traffic.webm'
        Url = 'https://upload.wikimedia.org/wikipedia/commons/b/b7/Berlin_Bundesautobahn_100_2026-03-25_mov03.webm'
        Sha256 = '91D52597960827B9AA6709EBBFCF5047160F83C31331D1F47EFDDD7D915D3D10'
    }
)

$targetDir = Join-Path $PSScriptRoot '..\datasets\open-road-demo'
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

foreach ($item in $items) {
    $target = Join-Path $targetDir $item.Name
    $currentHash = if (Test-Path -LiteralPath $target) {
        (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    } else {
        $null
    }

    if ($currentHash -ne $item.Sha256) {
        Write-Host "Downloading $($item.Name) from Wikimedia Commons..."
        & curl.exe --fail --location --silent --show-error --output $target $item.Url
        if ($LASTEXITCODE -ne 0) {
            throw "Download failed for $($item.Name)."
        }
        $currentHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    }

    if ($currentHash -ne $item.Sha256) {
        Remove-Item -LiteralPath $target -Force
        throw "SHA-256 verification failed for $($item.Name)."
    }

    Write-Host "Verified $($item.Name) ($currentHash)"
}
