$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { $uv = Join-Path $env:USERPROFILE '.local\bin\uv.exe' }
if (-not (Test-Path $uv)) { throw 'install uv from https://docs.astral.sh/uv/getting-started/installation/' }
& $uv venv --python 3.12 .venv
if ($LASTEXITCODE -ne 0) { throw 'model venv failed' }
& $uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'model packages failed to install' }
& $uv venv --python 3.12 interface/.venv
if ($LASTEXITCODE -ne 0) { throw 'ui venv failed' }
& $uv pip install --python interface/.venv/Scripts/python.exe -r interface/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'ui packages failed to install' }
