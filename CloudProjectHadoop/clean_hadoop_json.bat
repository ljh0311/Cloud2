@echo off
setlocal enabledelayedexpansion

REM Set analysis directory path
set "ANALYSIS_DIR=..\data\analysis"
set "OUTPUT_DIR=..\data\processed_data"
set "TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=!TIMESTAMP: =0!"

echo Processing analysis directories from: %ANALYSIS_DIR%

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Function to process and convert Hadoop output files
:ProcessAnalysisFile
set "INPUT_DIR=%~1"
set "ANALYSIS_TYPE=%~2"
set "BASE_NAME=%~3"
set "OUTPUT_FILE=%OUTPUT_DIR%\!BASE_NAME!_%ANALYSIS_TYPE%_%TIMESTAMP%.json"

if exist "%INPUT_DIR%\part-*" (
    echo Processing %ANALYSIS_TYPE% data from !INPUT_DIR!...
    type "%INPUT_DIR%\part-*" > "!OUTPUT_FILE!.tmp"
    
    REM Convert based on analysis type
    if "%ANALYSIS_TYPE%"=="location" (
        powershell -Command "$content = Get-Content '!OUTPUT_FILE!.tmp' -Raw; $lines = $content -split '\r?\n' | Where-Object {$_}; $locations = @(foreach ($line in $lines) { if ($line -match 'location:(.+?)\t(.+)') { @{ 'name' = $matches[1].Trim(); 'count' = [int]$matches[2].Trim(); 'coordinates' = switch ($matches[1].Trim()) { 'cte' { @{'lat'=1.3521; 'lng'=103.8198} }; 'changi' { @{'lat'=1.3644; 'lng'=103.9915} }; 'sle' { @{'lat'=1.3889; 'lng'=103.8516} }; 'pie' { @{'lat'=1.3404; 'lng'=103.7717} }; 'aye' { @{'lat'=1.2789; 'lng'=103.7577} }; 'woodlands' { @{'lat'=1.4382; 'lng'=103.7891} }; 'tampines' { @{'lat'=1.3496; 'lng'=103.9568} }; 'amk' { @{'lat'=1.3691; 'lng'=103.8454} }; 'tpe' { @{'lat'=1.3666; 'lng'=103.8877} }; 'bke' { @{'lat'=1.3801; 'lng'=103.7740} }; default { @{'lat'=1.3521; 'lng'=103.8198} } } } } }); @{'locations' = $locations; 'timestamp' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')} | ConvertTo-Json -Depth 10 | Set-Content '!OUTPUT_FILE!'"
    ) else if "%ANALYSIS_TYPE%"=="traffic" (
        powershell -Command "$content = Get-Content '!OUTPUT_FILE!.tmp' -Raw; $lines = $content -split '\r?\n' | Where-Object {$_}; $incidents = @(foreach ($line in $lines) { if ($line -match 'keyword:(.+?)\t(.+)') { @{ 'type' = $matches[1].Trim(); 'count' = [int]$matches[2].Trim() } } elseif ($line -match 'school:(.+?)\t(.+)') { @{ 'type' = 'school_' + $matches[1].Trim(); 'count' = [int]$matches[2].Trim() } } }); @{'incidents' = $incidents; 'timestamp' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')} | ConvertTo-Json -Depth 10 | Set-Content '!OUTPUT_FILE!'"
    ) else if "%ANALYSIS_TYPE%"=="trend" (
        powershell -Command "$content = Get-Content '!OUTPUT_FILE!.tmp' -Raw; $lines = $content -split '\r?\n' | Where-Object {$_}; $trends = @(foreach ($line in $lines) { if ($line -match 'keyword:(.+?)\t(.+)') { @{ 'keyword' = $matches[1].Trim(); 'count' = [int]$matches[2].Trim() } } elseif ($line -match 'school:(.+?)\t(.+)') { @{ 'keyword' = 'school_' + $matches[1].Trim(); 'count' = [int]$matches[2].Trim() } } }); @{'trends' = $trends; 'timestamp' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')} | ConvertTo-Json -Depth 10 | Set-Content '!OUTPUT_FILE!'"
    ) else if "%ANALYSIS_TYPE%"=="sentiment" (
        powershell -Command "$content = Get-Content '!OUTPUT_FILE!.tmp' -Raw; $lines = $content -split '\r?\n' | Where-Object {$_}; $sentiments = @(foreach ($line in $lines) { if ($line -match 'sentiment:(.+?)\t(.+)') { @{ 'sentiment' = $matches[1].Trim(); 'count' = [int]$matches[2].Trim(); 'percentage' = 0 } } }); $total = ($sentiments | Measure-Object -Property count -Sum).Sum; $sentiments = $sentiments | ForEach-Object { $_.percentage = [math]::Round($_.count / $total * 100, 2); $_ }; @{'sentiments' = $sentiments; 'total' = $total; 'timestamp' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')} | ConvertTo-Json -Depth 10 | Set-Content '!OUTPUT_FILE!'"
    ) else if "%ANALYSIS_TYPE%"=="brands" (
        powershell -Command "$content = Get-Content '!OUTPUT_FILE!.tmp' -Raw; $lines = $content -split '\r?\n' | Where-Object {$_}; $brandData = @{}; foreach ($line in $lines) { if ($line -match '(brand_comment|total|brand):(.+?)\t(.+)') { $type = $matches[1]; $brand = $matches[2].Trim(); $count = [int]$matches[3]; if (-not $brandData.ContainsKey($brand)) { $brandData[$brand] = @{'brand' = $brand; 'comments' = 0; 'total' = 0; 'rank' = 0} }; switch ($type) { 'brand_comment' { $brandData[$brand].comments = $count }; 'total' { $brandData[$brand].total = $count }; 'brand' { $brandData[$brand].rank = $count } } } }; $brands = @($brandData.Values | Sort-Object rank); @{'brands' = $brands; 'timestamp' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')} | ConvertTo-Json -Depth 10 | Set-Content '!OUTPUT_FILE!'"
    )
    
    del "!OUTPUT_FILE!.tmp"
    echo Created: !OUTPUT_FILE!
)
goto :eof

REM Find and process all analysis directories
for /d %%D in ("%ANALYSIS_DIR%\*") do (
    set "DIRNAME=%%~nxD"
    
    REM Extract base name and analysis type
    for /f "tokens=1-6 delims=_" %%a in ("!DIRNAME!") do (
        set "BASE_NAME=%%a_%%b_%%c"
        set "ANALYSIS_TYPE=%%d"
        
        REM Process the analysis file
        call :ProcessAnalysisFile "%%D" "!ANALYSIS_TYPE!" "!BASE_NAME!"
    )
)

echo.
echo Processing complete. Files saved in %OUTPUT_DIR%:
dir /b "%OUTPUT_DIR%\*.json"

REM Create metadata file for visualization
echo Creating metadata file...
powershell -Command "$files = @{}; Get-ChildItem '%ANALYSIS_DIR%' -Directory | ForEach-Object { if ($_.Name -match '(.+?)_(\d+)_(\d+)_(.+?)_') { $files[$matches[4]] = '%OUTPUT_DIR%\' + $_.Name + '_%TIMESTAMP%.json' } }; @{'dataset'='%BASE_NAME%'; 'timestamp'='%TIMESTAMP%'; 'analysis_date'='%date%'; 'analysis_time'='%time%'; 'files'=$files; 'summary'=@{'total_locations'=0; 'total_incidents'=0; 'sentiment_distribution'=@{}; 'top_brands'=@()}} | ConvertTo-Json -Depth 10 | Set-Content '%OUTPUT_DIR%\%BASE_NAME%_metadata_%TIMESTAMP%.json'"

echo Metadata file created: %OUTPUT_DIR%\%BASE_NAME%_metadata_%TIMESTAMP%.json

REM Create visualization data index
echo Creating visualization index...
powershell -Command "$analyses = @(Get-ChildItem '%ANALYSIS_DIR%' -Directory | Where-Object { $_.Name -match '(.+?)_(\d+)_(\d+)_location_' } | ForEach-Object { @{'id'=$matches[1]+'_'+$matches[2]+'_'+$matches[3]; 'date'=$matches[2]; 'time'=$matches[3]; 'metadata'='%OUTPUT_DIR%\'+$matches[1]+'_'+$matches[2]+'_'+$matches[3]+'_metadata_%TIMESTAMP%.json'} }); @{'analyses'=$analyses} | ConvertTo-Json -Depth 10 | Set-Content '%OUTPUT_DIR%\visualization_index.json'"

echo Visualization index created: %OUTPUT_DIR%\visualization_index.json
