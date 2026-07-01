# start.ps1
Write-Host "🚀 Starting NaviX Stack..." -ForegroundColor Cyan

# 1. Start Docker Containers
Write-Host "🐳 Building and starting Docker containers..." -ForegroundColor Gray
docker-compose up -d --build
if ($LASTEXITCODE -ne 0) { 
    Write-Host "❌ Docker failed to start. Please check if Docker Desktop is running." -ForegroundColor Red
    exit 
}

# 2. Get Local IP Address
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
