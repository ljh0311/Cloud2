@echo off
setlocal EnableDelayedExpansion

echo Visualization System Diagnostic and Repair Tool
echo ==============================================
echo.

set "WEB_DIR=%~dp0"
set "DATA_DIR=%~dp0.."
set "ANALYSIS_DIR=%DATA_DIR%\analysis"
set "INDEX_FILE=%WEB_DIR%visualizations\data\analyses_index.json"

echo Web Directory: %WEB_DIR%
echo Data Directory: %DATA_DIR%
echo Analysis Directory: %ANALYSIS_DIR%
echo Index File: %INDEX_FILE%
echo.

:: Step 1: Check if directories and index file exist
echo [1/6] Checking if required directories and files exist...
if not exist "%ANALYSIS_DIR%" (
    echo ERROR: Analysis directory does not exist at %ANALYSIS_DIR%
    echo Please ensure your folder structure is correct.
    goto :error
) else (
    echo [✓] Analysis directory exists.
)

if not exist "%WEB_DIR%visualizations\data" (
    echo [!] Visualizations data directory doesn't exist, creating it...
    mkdir "%WEB_DIR%visualizations\data"
    echo [✓] Created visualizations data directory.
) else (
    echo [✓] Visualizations data directory exists.
)

:: Step 2: Check if the PowerShell script exists to generate the index
echo.
echo [2/6] Checking if list_analyses.ps1 exists...
if not exist "%ANALYSIS_DIR%\list_analyses.ps1" (
    echo [!] list_analyses.ps1 script not found, creating it...
    (
        echo # Script to list all analysis directories and generate an index
        echo # This is used by the visualization system to locate analysis results
        echo.
        echo $analysisDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        echo $outputDir = "$analysisDir\..\web\visualizations\data"
        echo $outputFile = "$outputDir\analyses_index.json"
        echo.
        echo Write-Host "Checking for analysis directories in: $analysisDir"
        echo.
        echo # Create output directory if it doesn't exist
        echo if (^!(Test-Path $outputDir^)^) {
        echo     Write-Host "Creating output directory: $outputDir"
        echo     New-Item -ItemType Directory -Path $outputDir -Force ^| Out-Null
        echo }
        echo.
        echo # Get all directories matching the pattern
        echo $dirs = Get-ChildItem -Path $analysisDir -Directory ^| Where-Object { 
        echo     $_.Name -match '^(.+)_(\d{8}_\d{6})_(.+)_(\d{8}_\d{6})$' 
        echo }
        echo.
        echo $analyses = @^(^)
        echo.
        echo foreach ($dir in $dirs^) {
        echo     Write-Host "Processing directory: $($dir.Name^)"
        echo     
        echo     # Extract components from directory name
        echo     if ($dir.Name -match '^(.+)_(\d{8}_\d{6})_(.+)_(\d{8}_\d{6})$'^) {
        echo         $dataset = $matches[1]
        echo         $dataDate = $matches[2]
        echo         $analysisType = $matches[3]
        echo         $runDate = $matches[4]
        echo         
        echo         # Check if visualization/summary.json exists
        echo         $summaryFile = Join-Path -Path $dir.FullName -ChildPath "visualization\summary.json"
        echo         $summaryExists = Test-Path $summaryFile
        echo         
        echo         if ($summaryExists^) {
        echo             Write-Host "  Summary file exists for $analysisType"
        echo         } else {
        echo             Write-Host "  WARNING: Summary file missing for $analysisType"
        echo         }
        echo         
        echo         # Create relative path from web directory to the summary file
        echo         $relativePath = "../analysis/" + $dir.Name + "/visualization/summary.json"
        echo         
        echo         # Create an analysis entry
        echo         $analysis = @{
        echo             id = $dir.Name
        echo             run_date = $runDate
        echo             data_date = $dataDate
        echo             analysis_type = $analysisType
        echo             dataset = $dataset
        echo             summary_file = $relativePath
        echo             display_name = "$analysisType analysis of $dataset ^($runDate^)"
        echo         }
        echo         
        echo         $analyses += $analysis
        echo     } else {
        echo         Write-Host "  WARNING: Directory name doesn't match expected pattern"
        echo     }
        echo }
        echo.
        echo # Create the JSON object
        echo $json = @{
        echo     timestamp = ^(Get-Date -Format "yyyy-MM-dd HH:mm:ss"^)
        echo     analyses = $analyses
        echo     count = $analyses.Count
        echo }
        echo.
        echo # Save to JSON file
        echo $json ^| ConvertTo-Json -Depth 10 ^| Set-Content $outputFile
        echo.
        echo Write-Host "Found $($analyses.Count^) matching directories"
        echo Write-Host "Analysis index saved to: $outputFile"
    ) > "%ANALYSIS_DIR%\list_analyses.ps1"
    echo [✓] Created list_analyses.ps1 script.
) else (
    echo [✓] list_analyses.ps1 script exists.
)

:: Step 3: Check for update_index.bat
echo.
echo [3/6] Checking for update_index.bat...
if not exist "%ANALYSIS_DIR%\update_index.bat" (
    echo [!] update_index.bat script not found, creating it...
    (
        echo @echo off
        echo echo Running list_analyses.ps1 to generate analysis index...
        echo.
        echo powershell -ExecutionPolicy Bypass -File "%%~dp0list_analyses.ps1"
        echo.
        echo if errorlevel 1 ^(
        echo     echo ERROR: Failed to generate analysis index.
        echo     pause
        echo     exit /b 1
        echo ^)
        echo.
        echo echo.
        echo echo Successfully generated analysis index.
        echo echo.
        echo pause
    ) > "%ANALYSIS_DIR%\update_index.bat"
    echo [✓] Created update_index.bat script.
) else (
    echo [✓] update_index.bat script exists.
)

:: Step 4: Generate the index file
echo.
echo [4/6] Generating the analysis index file...
powershell -ExecutionPolicy Bypass -File "%ANALYSIS_DIR%\list_analyses.ps1"
if errorlevel 1 (
    echo ERROR: Failed to generate analysis index.
    goto :error
) else (
    echo [✓] Successfully generated analysis index.
)

:: Step 5: Verify that summary files exist
echo.
echo [5/6] Verifying summary files exist in each analysis directory...
set "MISSING_SUMMARY=0"

for /f "tokens=*" %%a in ('powershell -ExecutionPolicy Bypass -Command "& {Get-Content -Raw '%INDEX_FILE%' | ConvertFrom-Json | ForEach-Object { $_.analyses } | ForEach-Object { $_.id } }"') do (
    if not exist "%ANALYSIS_DIR%\%%a\visualization\summary.json" (
        echo [!] WARNING: Missing summary file for %%a
        set "MISSING_SUMMARY=1"
    ) else (
        echo [✓] Summary file exists for %%a
    )
)

if %MISSING_SUMMARY% EQU 1 (
    echo.
    echo WARNING: Some analysis directories are missing summary files.
    echo The visualization system may not work correctly for those analyses.
    echo.
) else (
    echo.
    echo [✓] All analysis directories have summary files.
)

:: Step 6: Create simple test HTML
echo.
echo [6/6] Creating test HTML to verify file access...
(
    echo ^<!DOCTYPE html^>
    echo ^<html^>
    echo ^<head^>
    echo     ^<title^>Analysis Files Test^</title^>
    echo     ^<style^>
    echo         body { font-family: Arial, sans-serif; margin: 20px; }
    echo         .success { color: green; }
    echo         .error { color: red; }
    echo         .loading { color: blue; }
    echo         .file-path { font-family: monospace; background: #f5f5f5; padding: 2px 5px; }
    echo     ^</style^>
    echo ^</head^>
    echo ^<body^>
    echo     ^<h1^>Analysis Files Test^</h1^>
    echo     
    echo     ^<h2^>Index File Test^</h2^>
    echo     ^<div id="index-test"^>^<span class="loading"^>Testing...^</span^>^</div^>
    echo     
    echo     ^<h2^>Summary Files Test^</h2^>
    echo     ^<div id="summary-test"^>^<span class="loading"^>Loading index...^</span^>^</div^>
    echo     
    echo     ^<script^>
    echo         // Test index file
    echo         async function testIndexFile() {
    echo             const testDiv = document.getElementById('index-test');
    echo             
    echo             try {
    echo                 const response = await fetch('./visualizations/data/analyses_index.json');
    echo                 
    echo                 if (response.ok) {
    echo                     const data = await response.json();
    echo                     testDiv.innerHTML = `
    echo                         ^<p class="success"^>✓ Successfully loaded index file^</p^>
    echo                         ^<p^>Found ${data.analyses.length} analyses in the index file.^</p^>
    echo                         ^<p^>Index file timestamp: ${data.timestamp}^</p^>
    echo                     `;
    echo                     return data;
    echo                 } else {
    echo                     testDiv.innerHTML = `
    echo                         ^<p class="error"^>✗ Failed to load index file. Status: ${response.status}^</p^>
    echo                         ^<p^>Path tried: ^<span class="file-path"^>./visualizations/data/analyses_index.json^</span^>^</p^>
    echo                     `;
    echo                     return null;
    echo                 }
    echo             } catch (error) {
    echo                 testDiv.innerHTML = `
    echo                     ^<p class="error"^>✗ Error loading index file: ${error.message}^</p^>
    echo                     ^<p^>Path tried: ^<span class="file-path"^>./visualizations/data/analyses_index.json^</span^>^</p^>
    echo                 `;
    echo                 return null;
    echo             }
    echo         }
    echo         
    echo         // Test summary files
    echo         async function testSummaryFiles(indexData) {
    echo             const testDiv = document.getElementById('summary-test');
    echo             
    echo             if (!indexData) {
    echo                 testDiv.innerHTML = `^<p class="error"^>✗ Cannot test summary files - index file not loaded^</p^>`;
    echo                 return;
    echo             }
    echo             
    echo             testDiv.innerHTML = '';
    echo             
    echo             let successCount = 0;
    echo             let failCount = 0;
    echo             
    echo             for (const analysis of indexData.analyses) {
    echo                 const summaryDiv = document.createElement('div');
    echo                 summaryDiv.innerHTML = `^<p^>Testing ${analysis.analysis_type} (${analysis.id})... ^<span class="loading"^>Loading...^</span^>^</p^>`;
    echo                 testDiv.appendChild(summaryDiv);
    echo                 
    echo                 try {
    echo                     const response = await fetch(analysis.summary_file);
    echo                     
    echo                     if (response.ok) {
    echo                         successCount++;
    echo                         summaryDiv.innerHTML = `
    echo                             ^<p class="success"^>✓ Successfully loaded summary for ${analysis.analysis_type}^</p^>
    echo                             ^<p^>Path: ^<span class="file-path"^>${analysis.summary_file}^</span^>^</p^>
    echo                         `;
    echo                     } else {
    echo                         failCount++;
    echo                         summaryDiv.innerHTML = `
    echo                             ^<p class="error"^>✗ Failed to load summary for ${analysis.analysis_type}. Status: ${response.status}^</p^>
    echo                             ^<p^>Path: ^<span class="file-path"^>${analysis.summary_file}^</span^>^</p^>
    echo                         `;
    echo                     }
    echo                 } catch (error) {
    echo                     failCount++;
    echo                     summaryDiv.innerHTML = `
    echo                         ^<p class="error"^>✗ Error loading summary for ${analysis.analysis_type}: ${error.message}^</p^>
    echo                         ^<p^>Path: ^<span class="file-path"^>${analysis.summary_file}^</span^>^</p^>
    echo                     `;
    echo                 }
    echo             }
    echo             
    echo             // Add summary
    echo             const summaryDiv = document.createElement('div');
    echo             summaryDiv.style.marginTop = '20px';
    echo             summaryDiv.style.padding = '10px';
    echo             summaryDiv.style.background = '#f5f5f5';
    echo             summaryDiv.style.borderRadius = '5px';
    echo             
    echo             if (failCount === 0) {
    echo                 summaryDiv.innerHTML = `^<p class="success"^>✓ All ${successCount} summary files loaded successfully!^</p^>`;
    echo             } else {
    echo                 summaryDiv.innerHTML = `
    echo                     ^<p^>^<strong^>Summary:^</strong^>^</p^>
    echo                     ^<p class="success"^>✓ Successfully loaded: ${successCount} files^</p^>
    echo                     ^<p class="error"^>✗ Failed to load: ${failCount} files^</p^>
    echo                 `;
    echo             }
    echo             
    echo             testDiv.appendChild(summaryDiv);
    echo         }
    echo         
    echo         // Run tests
    echo         async function runTests() {
    echo             const indexData = await testIndexFile();
    echo             await testSummaryFiles(indexData);
    echo         }
    echo         
    echo         // Run tests when page loads
    echo         window.onload = runTests;
    echo     ^</script^>
    echo ^</body^>
    echo ^</html^>
) > "%WEB_DIR%\test_analysis_files.html"

echo [✓] Created test_analysis_files.html for verifying file access.
echo.
echo All steps completed!
echo.
echo To test the visualization system:
echo 1. Open a web browser
echo 2. Navigate to http://localhost:8000/data/web/test_analysis_files.html
echo 3. If there are any errors, follow the instructions to fix them.
echo.
echo You can also test the visualization directly at:
echo http://localhost:8000/data/web/visualizations.html
echo.
echo Need to start a server? Run start_server.bat to start a simple HTTP server.
echo.
goto :end

:error
echo.
echo The script encountered an error. Please fix the issues and try again.
echo.

:end
pause 