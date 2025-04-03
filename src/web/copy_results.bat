@echo off
setlocal enabledelayedexpansion

echo Singapore Traffic Analysis - Copy Results to Web Directory
echo --------------------------------------------------------
echo.

REM Set base directories (adjust these paths according to your setup)
set "ANALYSIS_DIR=..\..\data\analysis"
set "WEB_DATA_DIR=data"

REM Create directories if they don't exist
if not exist "%WEB_DATA_DIR%" mkdir "%WEB_DATA_DIR%"

REM Get timestamp for this run
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%"

echo Using timestamp: %TIMESTAMP%
echo.

echo Copying analysis results to web data directory...
echo.

REM List analysis folders
for /d %%D in ("%ANALYSIS_DIR%\*") do (
    echo Processing %%~nxD

    REM Check for visualization/summary.json files
    if exist "%%D\visualization\summary.json" (
        echo Found visualization data in %%~nxD
        
        REM Create target directory
        if not exist "%WEB_DATA_DIR%\%%~nxD" mkdir "%WEB_DATA_DIR%\%%~nxD"
        
        REM Copy the summary.json file
        copy "%%D\visualization\summary.json" "%WEB_DATA_DIR%\%%~nxD\summary.json" > nul
        echo - Copied to %WEB_DATA_DIR%\%%~nxD\summary.json
    ) else (
        echo No visualization data found in %%~nxD
    )
    echo.
)

echo Creating datasets index...
echo.

REM Generate a datasets.json file with all available datasets
echo { "datasets": [ > "%WEB_DATA_DIR%\datasets.json"

set "first=true"
for /d %%D in ("%WEB_DATA_DIR%\*") do (
    if "!first!"=="true" (
        set "first=false"
    ) else (
        echo , >> "%WEB_DATA_DIR%\datasets.json"
    )
    
    REM Extract parts from directory name
    set "fullname=%%~nxD"
    
    echo   { >> "%WEB_DATA_DIR%\datasets.json"
    echo     "id": "!fullname!", >> "%WEB_DATA_DIR%\datasets.json"
    echo     "name": "!fullname!", >> "%WEB_DATA_DIR%\datasets.json"
    echo     "path": "%%D" >> "%WEB_DATA_DIR%\datasets.json"
    echo   } >> "%WEB_DATA_DIR%\datasets.json"
)

echo ] } >> "%WEB_DATA_DIR%\datasets.json"

echo Operation complete!
echo.
echo You can now view the dashboard at:
echo http://localhost:8000/src/web/templates/simple_visualizations.html
echo (after starting the web server with start_web_server.bat)
echo.
pause 