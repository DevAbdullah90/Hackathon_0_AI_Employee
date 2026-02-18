@echo off
REM Start AI Employee Gold Tier Automation System
REM This script starts the complete workflow orchestrator

echo ============================================================
echo     AI Employee - Starting Gold Tier Automation System
echo ============================================================
echo.

REM Set Python path (adjust if needed)
set PYTHON_PATH=python

REM Set vault path
REM Set vault path
set VAULT_PATH=c:\Users\hp\OneDrive\Desktop\Hackathon_AI_Employee

echo Starting Workflow Orchestrator...
echo Vault: %VAULT_PATH%
echo.

REM Change to vault directory
cd /d "%VAULT_PATH%"

REM Install required packages if needed
echo Checking dependencies...
%PYTHON_PATH% -m pip install -r requirements.txt

echo.
echo ============================================================
echo All dependencies checked. Starting main system...
echo ============================================================
echo.
echo The system will now:
echo   - Monitor the 'Approved' folder for files to process
echo   - Run periodic tasks (hourly, daily, weekly)
echo   - Check Reddit, Twitter, LinkedIn for opportunities
echo   - Generate content automatically
echo   - Create CEO briefings
echo.
echo Press Ctrl+C to stop the system gracefully.
echo ============================================================
echo.

REM Start the workflow orchestrator
REM Start the workflow orchestrator
set PYTHONPATH=%VAULT_PATH%;%VAULT_PATH%\src
%PYTHON_PATH% src/core/workflow_orchestrator.py "%VAULT_PATH%"

echo.
echo ============================================================
echo System stopped.
echo ============================================================
echo.
pause
