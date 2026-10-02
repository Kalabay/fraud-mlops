$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$docker = (Get-Command docker -ErrorAction SilentlyContinue).Source
if (-not $docker) { throw 'docker not found. check installation and PATH' }
if (-not (Test-Path fraud_detector/train_data/train.csv)) { throw 'file not found: fraud_detector/train_data/train.csv' }
& $docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'docker is not ready. start docker desktop' }
& $docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw 'start failed. see error above' }
& $docker compose ps
Write-Host 'interface: http://localhost:8501'
Write-Host 'kafka ui: http://localhost:8081'
