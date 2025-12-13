# SchedularV3 Automated Test Agent Launcher (PowerShell)
# Comprehensive testing with detailed logging

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SchedularV3 Automated Test Agent" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting automated testing..." -ForegroundColor Green
Write-Host "This will test all features with full logging and screenshot capture." -ForegroundColor White
Write-Host ""
Write-Host "Test Phases:" -ForegroundColor Yellow
Write-Host "  1. GUI Tests          - UI elements and interactions" -ForegroundColor White
Write-Host "  2. Transcript Tests   - Transcript loading and GPA validation" -ForegroundColor White
Write-Host "  3. Algorithm Tests    - All scheduler algorithms" -ForegroundColor White
Write-Host "  4. Integration Tests  - Complete workflows" -ForegroundColor White
Write-Host "  5. Stress Tests       - Random monkey testing" -ForegroundColor White
Write-Host ""
Write-Host "Reports will be generated in: tests\logs\reports\" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to SchedularV3 directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Join-Path $scriptPath "..\\.."
Set-Location $projectRoot

# Run the test agent
python tests\automated_agent\run_tests.py

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Reports:" -ForegroundColor Yellow
Write-Host "  HTML Report:   tests\logs\reports\test_report.html" -ForegroundColor White
Write-Host "  JSON Logs:     tests\logs\agent_logs\" -ForegroundColor White
Write-Host "  Screenshots:   tests\logs\screenshots\" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Open HTML report if it exists
$reportPath = "tests\logs\reports\test_report.html"
if (Test-Path $reportPath) {
    Write-Host "Opening HTML report in browser..." -ForegroundColor Green
    Start-Process $reportPath
}

Read-Host "Press Enter to exit"

