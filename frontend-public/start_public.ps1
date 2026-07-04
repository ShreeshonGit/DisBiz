# start_public.ps1
# Startup script for Public Customer Portal on Windows (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     STARTING FRONTEND PUBLIC PORTAL     " -ForegroundColor Cyan
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
Write-Host "`nPublic Portal runs at: http://localhost:3002" -ForegroundColor Green
Write-Host "=========================================`n" -ForegroundColor Cyan

# 4. Start Next.js dev server
npm run dev
