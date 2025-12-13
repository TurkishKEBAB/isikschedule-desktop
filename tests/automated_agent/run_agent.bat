@echo off
REM SchedularV3 Automated Test Agent Launcher
REM This script runs the comprehensive automated testing suite

echo ================================================================================
echo SchedularV3 Automated Test Agent
echo ================================================================================
echo.
echo Starting automated testing...
echo This will test all features with full logging and screenshot capture.
echo.
echo Test phases:
echo   1. GUI Tests
echo   2. Transcript Tests
echo   3. Algorithm Tests
echo   4. Integration Tests
echo   5. Stress Tests
echo.
echo Reports will be generated in: tests\logs\reports\
echo.
echo ================================================================================
echo.

REM Change to SchedularV3 directory
cd /d "%~dp0..\.."

REM Run the test agent
python tests\automated_agent\run_tests.py

echo.
echo ================================================================================
echo Testing complete!
echo.
echo View reports:
echo   HTML: tests\logs\reports\test_report.html
echo   JSON: tests\logs\agent_logs\
echo   Screenshots: tests\logs\screenshots\
echo ================================================================================
echo.

pause

