@echo off
echo Fixing the visualization system...
echo.

REM Set paths
set "CURRENT_DIR=%~dp0"
set "PROJECT_ROOT=%CURRENT_DIR%..\..\"
set "ANALYSIS_DIR=%PROJECT_ROOT%data\analysis"
set "WEB_DATA_DIR=%PROJECT_ROOT%data\web\visualizations\data"

echo Current directory: %CURRENT_DIR%
echo Project root: %PROJECT_ROOT%
echo Analysis directory: %ANALYSIS_DIR%
echo Web data directory: %WEB_DATA_DIR%
echo.

REM Create the web data directory if it doesn't exist
if not exist "%WEB_DATA_DIR%" (
    echo Creating web data directory: %WEB_DATA_DIR%
    mkdir "%WEB_DATA_DIR%"
)

REM Run the PowerShell script to generate the index
echo Generating analyses index...
powershell -ExecutionPolicy Bypass -Command "& {$analysisDir = '%ANALYSIS_DIR%'; $outputDir = '%WEB_DATA_DIR%'; $outputFile = Join-Path $outputDir 'analyses_index.json'; Write-Host 'Output file will be:' $outputFile; $analysisFolders = Get-ChildItem -Path $analysisDir -Directory | Where-Object { $_.Name -match '^[a-zA-Z0-9_]+' }; $analyses = @(); foreach ($folder in $analysisFolders) { $summaryFiles = @((Join-Path $folder.FullName 'visualization\summary.json'), (Join-Path $folder.FullName 'summary.json')); $summaryFile = $summaryFiles | Where-Object { Test-Path $_ } | Select-Object -First 1; if ($summaryFile) { $dataset = $folder.Name; $dataDate = Get-Date -Format 'yyyyMMdd'; $analysisType = 'unknown'; $runDate = Get-Date -Format 'yyyyMMdd_HHmmss'; if ($folder.Name -match '^(.+?)_(\d+)_(\d+)_(.+?)_(\d+)_(\d+)') { $dataset = $matches[1]; $dataDate = \"$($matches[2])_$($matches[3])\"; $analysisType = $matches[4]; $runDate = \"$($matches[5])_$($matches[6])\"; }; $relPath = $summaryFile.Replace($analysisDir, '').TrimStart('\'); $analyses += @{ 'id' = $folder.Name; 'dataset' = $dataset; 'data_date' = $dataDate; 'analysis_type' = $analysisType; 'run_date' = $runDate; 'summary_file' = $relPath; 'display_name' = \"$analysisType analysis of $dataset ($runDate)\" }; } }; $result = @{ 'analyses' = $analyses; 'timestamp' = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'; 'count' = $analyses.Count }; $result | ConvertTo-Json -Depth 10 | Set-Content $outputFile; Write-Host \"Generated index with $($analyses.Count) analyses\"; }"

REM Check if the index file was created
if not exist "%WEB_DATA_DIR%\analyses_index.json" (
    echo ERROR: Failed to create the analyses index file!
    echo Please check the PowerShell output for errors.
    pause
    exit /b 1
)

echo Index file successfully created at:
echo %WEB_DATA_DIR%\analyses_index.json
echo.

echo Setup complete! You can now access the visualization at:
echo http://localhost:5000/visualizations.html
echo.

pause 