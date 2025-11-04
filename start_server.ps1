# Worker Stress Analysis - Web Server Startup Script
# PowerShell Version

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Worker Stress Analysis - Web Server" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv311\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv311" -ForegroundColor Yellow
    Write-Host "Then install dependencies: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv311\Scripts\Activate.ps1"

# Check if Flask is installed
try {
    python -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Flask not installed"
    }
} catch {
    Write-Host "ERROR: Flask not installed!" -ForegroundColor Red
    Write-Host "Please run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the application
Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard will be available at: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python app.py
