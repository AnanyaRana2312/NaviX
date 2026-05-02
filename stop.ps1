# stop.ps1
Write-Host "🛑 Stopping NaviX Stack..." -ForegroundColor Red

# 1. Stop Docker Containers
Write-Host "🐳 Shutting down Docker containers..." -ForegroundColor Gray
docker-compose down
if ($LASTEXITCODE -ne 0) { 
    Write-Host "⚠️ Docker down command encountered an issue, but continuing cleanup..." -ForegroundColor Yellow
}

# 2. Kill Streamlit/Python UI processes
Write-Host "🧹 Cleaning up background processes (Streamlit)..." -ForegroundColor Gray
$processes = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object { $_.CommandLine -like "*streamlit*scripts/demo_ui.py*" }
if ($processes) {
    foreach ($p in $processes) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Terminated background UI processes." -ForegroundColor Gray
} else {
    Write-Host "ℹ️ No background UI processes found." -ForegroundColor Gray
}

Write-Host "`n🏁 Everything stopped." -ForegroundColor Yellow
