@echo off
echo ============================================
echo AI Employee Automation System Launcher
echo ============================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install watchdog pyyaml python-dotenv tweepy playwright --quiet

echo.
echo Installing Playwright browsers (first time only)...
playwright install chromium --quiet 2>nul

echo.
echo ============================================
echo Starting Services...
echo ============================================
echo.

echo Starting Auto Processor (monitors Approved folder)...
start "Auto Processor" cmd /k "python auto_processor.py"

timeout /t 2 >nul

echo Starting Draft Generator (monitors Needs_Action folder)...
start "Draft Generator" cmd /k "python draft_generator.py"

echo.
echo ============================================
echo AI Employee Automation System Started!
echo ============================================
echo.
echo Services running:
echo   - Auto Processor: Watches Approved/ and posts to platforms
echo   - Draft Generator: Watches Needs_Action/ and creates drafts
echo.
echo Workflow:
echo   1. Files arrive in Needs_Action/
echo   2. Draft Generator creates drafts in Pending_Approval/
echo   3. Human reviews and moves approved files to Approved/
echo   4. Auto Processor posts to platforms and moves to Done/
echo.
echo Close all windows to stop the system.
echo.
pause
