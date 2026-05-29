$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
Set-Location $Backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

