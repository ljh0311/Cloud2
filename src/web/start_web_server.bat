@echo off
echo Starting HTTP server for the Singapore Traffic Analysis Dashboard...
echo.

REM Navigate to the project root (assuming this script is in src/web)
cd ..\..\

echo Server running at: http://localhost:8000/src/web/templates/simple_visualizations.html
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH
    echo Please install Python or add it to your PATH
    echo.
    pause
    exit /b
)

REM Start the server
python -m http.server 8000
pause 