@echo off
echo Starting simple HTTP server for testing...
echo.
echo This will serve files from the current directory
echo Open your browser and go to: http://localhost:8000/data/web/test_paths.html
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