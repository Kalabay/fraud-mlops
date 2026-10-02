$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& .venv/Scripts/python.exe scripts/check_model.py
if ($LASTEXITCODE -ne 0) { throw 'model check failed' }
