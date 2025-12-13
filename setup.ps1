#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SchedularV3 Project Setup Script for Windows PowerShell

.DESCRIPTION
    Automatically sets up the SchedularV3 project for use in PyCharm or command line.
    - Creates virtual environment if needed
    - Installs project in editable mode
    - Installs all dependencies
    - Verifies all imports work

.EXAMPLE
    PS> .\setup.ps1
#>

param(
    [switch]$Force = $false
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "SchedularV3 Project Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ProjectRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Check if Python is available
try {
    $PythonVersion = python --version 2>$null
    Write-Host "✓ Python found" -ForegroundColor Green
    Write-Host "  $PythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check if virtual environment exists
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    & $VenvActivate
} else {
    Write-Host "! Virtual environment not found at .venv" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    & $VenvActivate
    Write-Host "✓ Virtual environment created and activated" -ForegroundColor Green
}
Write-Host ""

# Install the project in editable mode
Write-Host "Installing SchedularV3 in editable mode..." -ForegroundColor Cyan
pip install -e . | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install project in editable mode" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Project installed successfully" -ForegroundColor Green
Write-Host ""

# Install development dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
$VerifyScript = @"
try:
    from core.models import Course
    from utils.schedule_metrics import SchedulerPrefs
    from algorithms.base_scheduler import BaseScheduler
    print('✓ All core imports successful')
except ImportError as e:
    print(f'ERROR: Import failed: {e}')
    exit(1)
"@

python -c $VerifyScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Some imports failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Final status
Write-Host "================================================" -ForegroundColor Green
Write-Host "✓ SETUP COMPLETE" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Reload your PyCharm project:" -ForegroundColor White
Write-Host "   File > Invalidate Caches > Invalidate and Restart" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Mark directories as sources:" -ForegroundColor White
Write-Host "   - Right-click core/ > Mark Directory as > Sources Root" -ForegroundColor Gray
Write-Host "   - Right-click utils/ > Mark Directory as > Sources Root" -ForegroundColor Gray
Write-Host "   - Right-click algorithms/ > Mark Directory as > Sources Root" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Set Python interpreter:" -ForegroundColor White
Write-Host "   File > Settings > Project > Python Interpreter" -ForegroundColor Gray
Write-Host "   Select: .venv\Scripts\python.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "All imports should now work correctly!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"

