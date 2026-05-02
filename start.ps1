# start.ps1
Write-Host "🚀 Starting NaviX Stack..." -ForegroundColor Cyan

# 1. Start Docker Containers
Write-Host "🐳 Building and starting Docker containers..." -ForegroundColor Gray
docker-compose up -d --build
if ($LASTEXITCODE -ne 0) { 
    Write-Host "❌ Docker failed to start. Please check if Docker Desktop is running." -ForegroundColor Red
    exit 
}

# 2. Start Streamlit UI in the background
Write-Host "📊 Starting Streamlit UI..." -ForegroundColor Green
$streamlitCmd = ".venv\Scripts\python.exe -m streamlit run scripts/demo_ui.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'NaviX Streamlit UI Starting...'; $streamlitCmd"

# Get Local IP Address
$localIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*vEthernet*" -and $_.InterfaceAlias -notlike "*VirtualBox*" } | Select-Object -First 1 -ExpandProperty IPAddress)

Write-Host ""
Write-Host "✅ All systems go!" -ForegroundColor Yellow
Write-Host "------------------------------------------------"
Write-Host "React Frontend (Local):   http://localhost:5173"
if ($localIp) {
    Write-Host "React Frontend (Network): http://$($localIp):5173"
}
Write-Host "Backend API:              http://localhost:8000"
Write-Host "------------------------------------------------"
Write-Host "Streamlit UI (Local):     http://localhost:8501"
if ($localIp) {
    Write-Host "Streamlit UI (Network):   http://$($localIp):8501"
}
Write-Host "------------------------------------------------"
