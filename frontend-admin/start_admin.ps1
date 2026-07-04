# start_admin.ps1
# Startup script for Admin Dashboard Frontend on Windows (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     STARTING FRONTEND ADMIN PORTAL      " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Clean build cache
Write-Host "Clearing Next.js build cache..." -ForegroundColor Green
npm run clean

# 2. Check node_modules and install if missing
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing node packages..." -ForegroundColor Green
    npm install
}

# 3. Print running URLs
Write-Host "`nAdmin Portal runs at: http://localhost:3000" -ForegroundColor Green
Write-Host "Automation Panel:     http://localhost:3000/automation" -ForegroundColor Green
Write-Host "=========================================`n" -ForegroundColor Cyan

# 4. Start Next.js dev server
npm run dev
