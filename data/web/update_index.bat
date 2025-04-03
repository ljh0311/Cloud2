@echo off
echo Creating index file for visualizations.html...
echo.

REM Set directories
set "ANALYSIS_DIR=%~dp0..\analysis"
set "INDEX_DIR=%~dp0visualizations\data"
set "INDEX_FILE=%INDEX_DIR%\analyses_index.json"
set "TEMP_FILE=%TEMP%\analyses_index.json"

echo Analysis directory: %ANALYSIS_DIR%
echo Output directory: %INDEX_DIR%
echo Output file: %INDEX_FILE%

REM Create output directory if it doesn't exist
if not exist "%INDEX_DIR%" (
    echo Creating output directory...
    mkdir "%INDEX_DIR%"
)

REM Run PowerShell to generate analyses index
echo Running PowerShell script to generate index...
powershell -ExecutionPolicy Bypass -Command "& {$analysisFolders = Get-ChildItem -Path '%ANALYSIS_DIR%' -Directory | Where-Object { $_.Name -match '^[a-zA-Z0-9_]+' }; $analyses = @(); foreach ($folder in $analysisFolders) { $summaryFiles = @((Join-Path $folder.FullName 'visualization\summary.json'), (Join-Path $folder.FullName 'summary.json')); $summaryFile = $summaryFiles | Where-Object { Test-Path $_ } | Select-Object -First 1; if ($summaryFile) { $dataset = $folder.Name; $dataDate = Get-Date -Format 'yyyyMMdd'; $analysisType = 'unknown'; $runDate = Get-Date -Format 'yyyyMMdd_HHmmss'; if ($folder.Name -match '^(.+?)_(\d+)_(\d+)_(.+?)_(\d+)_(\d+)') { $dataset = $matches[1]; $dataDate = '$($matches[2])_$($matches[3])'; $analysisType = $matches[4]; $runDate = '$($matches[5])_$($matches[6])'; }; $relPath = $summaryFile.Replace('%ANALYSIS_DIR%', '').TrimStart('\'); $analyses += @{ 'id' = $folder.Name; 'dataset' = $dataset; 'data_date' = $dataDate; 'analysis_type' = $analysisType; 'run_date' = $runDate; 'summary_file' = $relPath; 'display_name' = "$analysisType analysis of $dataset ($runDate)" }; } }; $result = @{ 'analyses' = $analyses; 'timestamp' = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'; 'count' = $analyses.Count }; $result | ConvertTo-Json -Depth 10 | Set-Content '%INDEX_FILE%'; Write-Host "Generated index with $($analyses.Count) analyses"; }"

REM Check if file was created
if exist "%INDEX_FILE%" (
    echo.
    echo Success! Index file created at:
    echo %INDEX_FILE%
    echo.
    echo You can now access the visualization at:
    echo http://localhost:5000/visualizations.html
) else (
    echo.
    echo ERROR: Failed to create index file!
    echo Please check the PowerShell output for errors.
    exit /b 1
)

pause 