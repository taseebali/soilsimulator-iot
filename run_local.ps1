# PowerShell script to run sensor simulator locally
# Usage: .\run_local.ps1

param(
    [Parameter(Mandatory=$false)]
    [int]$Interval = 120,
    
    [Parameter(Mandatory=$false)]
    [string]$DeviceId = "field_sensor_01",
    
    [Parameter(Mandatory=$false)]
    [string]$FieldName = "Field A - Tomatoes"
)

Write-Host "🌱 Starting Soil Sensor Simulator (Local Mode)" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  MQTT Broker: localhost:1883" -ForegroundColor Cyan
Write-Host "  Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host "  Field Name: $FieldName" -ForegroundColor Cyan
Write-Host "  Publish Interval: $Interval seconds" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated. Activating..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
}

# Check if Docker containers are running
Write-Host "🔍 Checking Docker containers..." -ForegroundColor Yellow
$mosquittoRunning = docker ps --filter "name=mqtt_broker" --filter "status=running" --format "{{.Names}}"

if ($mosquittoRunning -eq "mqtt_broker") {
    Write-Host "✅ Mosquitto broker is running" -ForegroundColor Green
} else {
    Write-Host "❌ Mosquitto broker is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start Docker services:" -ForegroundColor Yellow
    Write-Host "  cd docker" -ForegroundColor Cyan
    Write-Host "  docker-compose up -d" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') {
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Starting simulator... (Press Ctrl+C to stop)" -ForegroundColor Green
Write-Host ""

# Run the simulator
python soil_sensor_simulator.py `
    --broker localhost `
    --interval $Interval `
    --device-id $DeviceId `
    --field-name $FieldName `
    --verbose
