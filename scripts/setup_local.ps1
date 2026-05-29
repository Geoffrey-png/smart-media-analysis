$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$PipCache = Join-Path $Root ".cache\pip"
$NpmCache = Join-Path $Root ".cache\npm"

New-Item -ItemType Directory -Force -Path $PipCache, $NpmCache | Out-Null

Write-Host "项目根目录: $Root"
Write-Host "Python 虚拟环境: $Backend\.venv"
Write-Host "pip 缓存: $PipCache"
Write-Host "npm 缓存: $NpmCache"
Write-Host "node_modules: $Frontend\node_modules"

Set-Location $Backend
if (!(Test-Path ".\.venv\Scripts\python.exe")) {
  python -m venv .venv
}
.\.venv\Scripts\python -m pip install --cache-dir $PipCache -r requirements.txt
.\.venv\Scripts\python scripts\init_db.py

Set-Location $Frontend
npm install --cache $NpmCache

Write-Host "本地依赖安装完成。"

