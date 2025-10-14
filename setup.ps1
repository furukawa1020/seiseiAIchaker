# セットアップスクリプト（Windows PowerShell用）

Write-Host "=== RefSys セットアップ ===" -ForegroundColor Cyan
Write-Host ""

# Python バージョン確認
Write-Host "1. Python バージョン確認..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: Python がインストールされていません" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 仮想環境作成（オプション）
$createVenv = Read-Host "仮想環境を作成しますか？ (y/n)"
if ($createVenv -eq "y") {
    Write-Host "2. 仮想環境作成..." -ForegroundColor Yellow
    python -m venv venv
    
    Write-Host "仮想環境をアクティブ化..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
    Write-Host ""
}

# 依存関係インストール
Write-Host "3. 依存関係インストール..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: 依存関係のインストールに失敗しました" -ForegroundColor Red
    exit 1
}
Write-Host ""

# データベース初期化
Write-Host "4. データベース初期化..." -ForegroundColor Yellow
python -m refsys.db.init_db
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: データベースの初期化に失敗しました" -ForegroundColor Red
    exit 1
}
Write-Host ""

# テスト実行
Write-Host "5. システムテスト..." -ForegroundColor Yellow
$runTest = Read-Host "テストを実行しますか？ (y/n)"
if ($runTest -eq "y") {
    python test_system.py
}
Write-Host ""

Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. Web UI起動: python -m refsys server" -ForegroundColor White
Write-Host "  2. CLI使用:    python -m refsys --help" -ForegroundColor White
Write-Host "  3. ドキュメント: QUICKSTART.md を参照" -ForegroundColor White
Write-Host ""
