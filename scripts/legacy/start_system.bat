@echo off
echo Starting AI Employee System...

cd /d "c:\Users\hp\OneDrive\Desktop\Hackathon_AI_Employee"

echo Creating necessary directories...
if not exist "Logs" mkdir Logs
if not exist "Plans" mkdir Plans
if not exist "Pending_Approval" mkdir Pending_Approval
if not exist "Approved" mkdir Approved
if not exist "Rejected" mkdir Rejected

echo Starting AI Employee System Components...

echo Starting Scheduler...
start /min python scheduler.py

echo Starting MCP Server...
cd mcp\email-mcp
start /min cmd /k "npm install && node index.js"

echo System started successfully!
echo.
echo The following components are now running:
echo - Scheduler (runs tasks periodically)
echo - Email MCP Server (handles email operations)
echo.
echo Watchers are available in the watchers directory
echo LinkedIn posting functionality is available via linkedin_watcher.py
echo Plan creation is available via plan_creator.py
echo.
pause