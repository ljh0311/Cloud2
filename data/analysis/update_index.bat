@echo off
setlocal enabledelayedexpansion

REM Set path to the analysis folder
set ANALYSIS_DIR=%~dp0
set OUTPUT_DIR=%ANALYSIS_DIR%\..\web\visualizations\data
set INDEX_FILE=%OUTPUT_DIR%\analyses_index.json

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo Created output directory at %OUTPUT_DIR%
)

echo Building analysis index...
echo.

REM Start JSON file
echo { > "%INDEX_FILE%"
echo   "analyses": [ >> "%INDEX_FILE%"

set FIRST_ENTRY=true

REM Loop through each analysis directory
for /d %%D in ("%ANALYSIS_DIR%*") do (
    set DIR_NAME=%%~nxD
    
    REM Skip if it's not an analysis directory (batch files, etc.)
    echo !DIR_NAME! | findstr /r "^list_analyses\.ps1$ ^update_index\.bat$" >nul
    if errorlevel 1 (
        echo Processing !DIR_NAME!...
        
        REM Extract dataset and run date from directory name (format: dataset_datadate_rundate_analysis)
        for /f "tokens=1-4 delims=_" %%a in ("!DIR_NAME!") do (
            set DATASET=%%a
            set DATA_DATE=%%b
            set RUN_DATE=%%c
            set ANALYSIS_TYPE=%%d
            
            REM Check if analysis output file exists
            if exist "%%D\part-r-00000" (
                REM Add comma for all but the first entry
                if !FIRST_ENTRY! == true (
                    set FIRST_ENTRY=false
                ) else (
                    echo , >> "%INDEX_FILE%"
                )
                
                REM Create the JSON entry for this analysis
                echo     { >> "%INDEX_FILE%"
                echo       "dataset": "!DATASET!_!DATA_DATE!", >> "%INDEX_FILE%"
                echo       "data_date": "!DATA_DATE!", >> "%INDEX_FILE%"
                echo       "run_date": "!RUN_DATE!", >> "%INDEX_FILE%"
                echo       "analysis_type": "!ANALYSIS_TYPE!", >> "%INDEX_FILE%"
                echo       "summary_file": "/static/data/!DIR_NAME!/summary.json", >> "%INDEX_FILE%"
                echo       "output_dir": "../../data/analysis/!DIR_NAME!" >> "%INDEX_FILE%"
                echo     } >> "%INDEX_FILE%"
                
                REM Create summary JSON file if it doesn't exist
                set SUMMARY_DIR=%OUTPUT_DIR%\!DIR_NAME!
                set SUMMARY_FILE=!SUMMARY_DIR!\summary.json
                
                if not exist "!SUMMARY_DIR!" (
                    mkdir "!SUMMARY_DIR!"
                    echo Created summary directory at !SUMMARY_DIR!
                )
                
                if not exist "!SUMMARY_FILE!" (
                    echo Creating summary file for !DIR_NAME!...
                    echo { > "!SUMMARY_FILE!"
                    echo   "dataset": "!DATASET!_!DATA_DATE!", >> "!SUMMARY_FILE!"
                    echo   "data_date": "!DATA_DATE!", >> "!SUMMARY_FILE!"
                    echo   "run_date": "!RUN_DATE!", >> "!SUMMARY_FILE!"
                    echo   "analysis_type": "!ANALYSIS_TYPE!", >> "!SUMMARY_FILE!"
                    echo   "output_dir": "../../data/analysis/!DIR_NAME!" >> "!SUMMARY_FILE!"
                    echo } >> "!SUMMARY_FILE!"
                )
            )
        )
    )
)

REM Close the JSON file
echo   ] >> "%INDEX_FILE%"
echo } >> "%INDEX_FILE%"

echo.
echo Analysis index complete at %INDEX_FILE%
echo.

REM Display the analyses that were indexed
echo Found analyses:
type "%INDEX_FILE%"

echo.
echo Press any key to exit...
pause > nul 