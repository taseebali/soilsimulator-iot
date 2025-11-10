# PowerShell script to run sensor simulator with cloud configuration
# Usage: .\run_cloud.ps1 [GCP_VM_IP]

param(
    [Parameter(Mandatory=$false)]
    [string]$BrokerIP = $env:GCP_VM_IP,
    
    [Parameter(Mandatory=$false)]
    [int]$Interval = 120,
    
    [Parameter(Mandatory=$false)]
    [string]$DeviceId = "field_sensor_01",
    
    [Parameter(Mandatory=$false)]
    [string]$FieldName = "Field A - Tomatoes"
)

# Check if broker IP is provided
if ([string]::IsNullOrEmpty($BrokerIP)) {
    Write-Host "❌ Error: GCP VM IP not provided" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run_cloud.ps1 <GCP_VM_IP>" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or set environment variable:" -ForegroundColor Yellow
    Write-Host '  $env:GCP_VM_IP = "34.179.141.137"' -ForegroundColor Cyan
    Write-Host '  .\run_cloud.ps1' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -BrokerIP <IP>      MQTT broker IP (required)" -ForegroundColor Cyan
    Write-Host "  -Interval <seconds> Publish interval (default: 120)" -ForegroundColor Cyan
    Write-Host "  -DeviceId <id>      Device identifier" -ForegroundColor Cyan
    Write-Host "  -FieldName <name>   Field name" -ForegroundColor Cyan
    exit 1
}

Write-Host "🌱 Starting Soil Sensor Simulator (Cloud Mode)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  MQTT Broker: $BrokerIP:1883" -ForegroundColor Cyan
Write-Host "  Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host "  Field Name: $FieldName" -ForegroundColor Cyan
Write-Host "  Publish Interval: $Interval seconds" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated. Activating..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
}

# Test connection to broker
Write-Host "🔍 Testing connection to broker..." -ForegroundColor Yellow
$testResult = Test-NetConnection -ComputerName $BrokerIP -Port 1883 -WarningAction SilentlyContinue

if ($testResult.TcpTestSucceeded) {
    Write-Host "✅ Connection to broker successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot reach broker at ${BrokerIP}:1883" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check if GCP VM is running" -ForegroundColor Cyan
    Write-Host "  2. Verify firewall allows port 1883" -ForegroundColor Cyan
    Write-Host "  3. Ensure Mosquitto is running on VM" -ForegroundColor Cyan
    Write-Host "  4. Check VM external IP is correct" -ForegroundColor Cyan
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
    --broker $BrokerIP `
    --interval $Interval `
    --device-id $DeviceId `
    --field-name $FieldName `
    --verbose
