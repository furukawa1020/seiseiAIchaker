# 両方を同時に起動し、どちらかが落ちても再起動しないシンプル版
# start-dev-simple.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "RefSys Development Environment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Python環境のチェック
Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  $pythonVersion" -ForegroundColor Green

# Node.js環境のチェック
Write-Host "[2/3] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Node.js not found" -ForegroundColor Red
    exit 1
}
Write-Host "  Node.js $nodeVersion" -ForegroundColor Green

# 起動
Write-Host "[3/3] Starting servers..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend UI:  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# ブラウザを開く
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "To stop servers, press Ctrl+C in each terminal window" -ForegroundColor Yellow
Write-Host ""

# 2つの新しいウィンドウでサーバーを起動
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m refsys server"
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host "Servers launched in separate windows!" -ForegroundColor Green
Write-Host "Close the terminal windows to stop the servers." -ForegroundColor Yellow
