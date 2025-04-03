@echo off
REM =====================================================================
REM Singapore Traffic Analysis Hadoop Job Runner
REM This script runs the Hadoop job for different types of analysis with
REM timestamp filtering support.
REM =====================================================================

echo ===================================================================
echo Singapore Traffic Analysis Hadoop Job Runner
echo ===================================================================
echo.

REM Set default variables
set INPUT_FILE=
set ANALYSIS_TYPE=
set OUTPUT_DIR=
set START_TIME=
set END_TIME=
set JAR_FILE=

REM Parse command line arguments
if "%~1"=="" (
    echo Error: Missing input file
    goto usage
)
set INPUT_FILE=%~1

if "%~2"=="" (
    echo Error: Missing analysis type
    goto usage
)
set ANALYSIS_TYPE=%~2

if "%~3"=="" (
    echo Error: Missing output directory
    goto usage
)
set OUTPUT_DIR=%~3

REM Parse optional start time and end time
:parse_args
if "%~4"=="" goto continue_execution
if "%~4"=="--start-time" (
    if "%~5"=="" (
        echo Error: Missing start time value
        goto usage
    )
    set START_TIME=%~5
    shift
    shift
    goto parse_args
)
if "%~4"=="--end-time" (
    if "%~5"=="" (
        echo Error: Missing end time value
        goto usage
    )
    set END_TIME=%~5
    shift
    shift
    goto parse_args
)

:continue_execution
REM Map analysis type to JAR file
if /i "%ANALYSIS_TYPE%"=="sentiment" (
    set JAR_FILE=..\HadoopJar\TAsentiment.jar
) else if /i "%ANALYSIS_TYPE%"=="traffic" (
    set JAR_FILE=..\HadoopJar\TAtraffic.jar
) else if /i "%ANALYSIS_TYPE%"=="location" (
    set JAR_FILE=..\HadoopJar\TAlocation.jar
) else if /i "%ANALYSIS_TYPE%"=="brands" (
    set JAR_FILE=..\HadoopJar\TAbrands.jar
) else if /i "%ANALYSIS_TYPE%"=="trend" (
    set JAR_FILE=..\HadoopJar\TAtrend.jar
) else (
    echo Error: Unsupported analysis type: %ANALYSIS_TYPE%
    echo Supported types: sentiment, traffic, location, brands, trend
    exit /b 1
)

echo Input file: %INPUT_FILE%
echo Analysis type: %ANALYSIS_TYPE%
echo Output directory: %OUTPUT_DIR%
if defined START_TIME echo Start time: %START_TIME%
if defined END_TIME echo End time: %END_TIME%
echo JAR file: %JAR_FILE%
echo.

REM Check if input file exists
if not exist "%INPUT_FILE%" (
    echo Error: Input file does not exist: %INPUT_FILE%
    exit /b 1
)

REM Check if JAR file exists
if not exist "%JAR_FILE%" (
    echo Error: JAR file does not exist: %JAR_FILE%
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo Created output directory: %OUTPUT_DIR%
)

echo Starting Hadoop job...
echo.

REM Build the command based on whether start time and end time are provided
set CMD=hadoop jar "%JAR_FILE%" "%INPUT_FILE%" "%ANALYSIS_TYPE%" "%OUTPUT_DIR%"

if defined START_TIME (
    set CMD=%CMD% --start-time "%START_TIME%"
)

if defined END_TIME (
    set CMD=%CMD% --end-time "%END_TIME%"
)

echo Executing: %CMD%
echo.

REM Execute the command
call %CMD%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Hadoop job completed successfully
    echo Output is available in: %OUTPUT_DIR%
    
    REM Run the script to update the visualization index
    echo.
    echo Updating visualization index...
    call "..\data\analysis\update_index.bat"
    
    echo.
    echo Processing complete! You can now view the results in the web visualization dashboard.
) else (
    echo.
    echo Error: Hadoop job failed with error code %ERRORLEVEL%
)

exit /b %ERRORLEVEL%

:usage
echo.
echo Usage: run_hadoop_analysis.bat ^<input_file^> ^<analysis_type^> ^<output_dir^> [--start-time "YYYY-MM-DD HH:MM"] [--end-time "YYYY-MM-DD HH:MM"]
echo.
echo Analysis types: sentiment, traffic, location, brands, trend
echo.
echo Examples:
echo   run_hadoop_analysis.bat data.json sentiment output
echo   run_hadoop_analysis.bat data.json trend output --start-time "2025-04-01 00:00" --end-time "2025-04-30 23:59"
echo.
exit /b 1 