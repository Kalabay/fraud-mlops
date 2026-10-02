$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$docker = (Get-Command docker -ErrorAction SilentlyContinue).Source
if (-not $docker) { throw 'docker not found. check installation and PATH' }
& $docker compose down
