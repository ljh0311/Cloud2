@echo off
echo Running analysis index generator...
echo.

REM Check if PowerShell is available
powershell -Command "Get-ExecutionPolicy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PowerShell is not available on this system.
    echo Please make sure PowerShell is installed and in your PATH.
    pause
    exit /b 1
)

echo Creating analyses index file...

REM Run the PowerShell script with Bypass execution policy to ensure it can run
powershell -ExecutionPolicy Bypass -File "%~dp0list_analyses.ps1"

echo.
echo Index file creation complete!
echo You can now view the dashboard at http://localhost:5000
echo.
pause 