# start_backend.ps1
# Startup script for Backend FastAPI Service on Windows (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   STARTING DEALER DISCOVERY BACKEND     " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Activate Python Virtual Environment
$VenvPath = "..\venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "Activating virtual environment at $VenvPath..." -ForegroundColor Green
    . $VenvPath
} else {
    Write-Host "Warning: Virtual environment not found at $VenvPath. Using global python." -ForegroundColor Yellow
}

# 2. Check and install missing requirements
if (Test-Path "requirements.txt") {
    Write-Host "Installing missing pip packages from requirements.txt..." -ForegroundColor Green
    pip install -r requirements.txt
}

# 3. Print running URLs
Write-Host "`nBackend API runs at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation:    http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Alternative Docs:     http://127.0.0.1:8000/api/v1/docs" -ForegroundColor Green
Write-Host "=========================================`n" -ForegroundColor Cyan

# 4. Start Uvicorn Dev Server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
