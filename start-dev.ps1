# 両方を同時に起動するスクリプト
# start-dev.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "RefSys Development Environment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Python環境のチェック
Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  $pythonVersion" -ForegroundColor Green

# Node.js環境のチェック
Write-Host "[2/4] Checking Node.js environment..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Node.js $nodeVersion" -ForegroundColor Green

# フロントエンド依存関係のチェック
Write-Host "[3/4] Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
}
Write-Host "  Dependencies OK" -ForegroundColor Green

# 起動
Write-Host "[4/4] Starting servers..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend UI:  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# バックエンドを起動 (バックグラウンド)
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m refsys server
}

# フロントエンドを起動 (バックグラウンド)
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location frontend
    npm run dev
}

# ログをリアルタイムで表示
try {
    while ($true) {
        # バックエンドのログ
        $backendOutput = Receive-Job -Job $backendJob 2>&1
        if ($backendOutput) {
            Write-Host "[Backend] $backendOutput" -ForegroundColor Blue
        }
        
        # フロントエンドのログ
        $frontendOutput = Receive-Job -Job $frontendJob 2>&1
        if ($frontendOutput) {
            Write-Host "[Frontend] $frontendOutput" -ForegroundColor Magenta
        }
        
        Start-Sleep -Milliseconds 100
    }
}
finally {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob
    Stop-Job -Job $frontendJob
    Remove-Job -Job $backendJob
    Remove-Job -Job $frontendJob
    Write-Host "Done!" -ForegroundColor Green
}
