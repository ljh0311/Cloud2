@echo off
echo Fixing the analyses_index.json file paths for Flask application...
echo.

set "WEB_DIR=%~dp0"
set "DATA_DIR=%~dp0.."
set "ANALYSIS_DIR=%DATA_DIR%\analysis"
set "INDEX_FILE=%WEB_DIR%visualizations\data\analyses_index.json"
set "FLASK_STATIC_DIR=%~dp0..\..\src\web\static"
set "FLASK_INDEX_DIR=%FLASK_STATIC_DIR%\data"
set "TEMP_PS_SCRIPT=%TEMP%\fix_index_paths.ps1"

echo Web Directory: %WEB_DIR%
echo Data Directory: %DATA_DIR%
echo Analysis Directory: %ANALYSIS_DIR%
echo Index File: %INDEX_FILE%
echo Flask Static Directory: %FLASK_STATIC_DIR%
echo.

if not exist "%INDEX_FILE%" (
  echo ERROR: The analyses_index.json file doesn't exist at %INDEX_FILE%
  echo Please run update_index.bat first.
  pause
  exit /b 1
)

echo Creating Flask static data directory if it doesn't exist...
if not exist "%FLASK_INDEX_DIR%" (
  mkdir "%FLASK_INDEX_DIR%"
  echo Created directory: %FLASK_INDEX_DIR%
)

echo Creating fixed index file with paths for Flask...

:: First, check if all analysis directories exist
for /f "tokens=*" %%a in ('powershell -ExecutionPolicy Bypass -Command "Get-Content -Raw '%INDEX_FILE%' | ConvertFrom-Json | ForEach-Object { $_.analyses } | ForEach-Object { $_.id }"') do (
  if not exist "%ANALYSIS_DIR%\%%a" (
    echo WARNING: Analysis directory not found: %%a
    ) else (
    echo Found analysis directory: %%a
  )
)

:: Create a temporary PowerShell script
echo Creating temporary PowerShell script...
(
echo $json = Get-Content -Raw '%INDEX_FILE%' ^| ConvertFrom-Json
echo $analysisDir = '%ANALYSIS_DIR%' -replace '\\', '/'
echo.
echo foreach ($analysis in $json.analyses^) {
echo  $id = $analysis.id
echo  # Check if the summary file exists
echo  $summaryPath = Join-Path -Path '%ANALYSIS_DIR%' -ChildPath ($id + '/visualization/summary.json'^)
echo.
echo  # Flask static path
echo  $staticPath = '/static/data/' + $id + '.json'
echo.
echo  if (Test-Path $summaryPath^) {
echo  Write-Host ('Summary file found for ' + $id^)
echo.
echo  # Set the path for Flask
echo  $analysis.summary_file = $staticPath
echo.
echo  # Copy the summary file to Flask static folder
echo  $destinationFile = '%FLASK_INDEX_DIR%\' + $id + '.json'
echo  Write-Host ('Copying summary file to: ' + $destinationFile^)
echo  Copy-Item -Path $summaryPath -Destination $destinationFile -Force
echo  } else {
echo  Write-Host ('Summary file NOT found for ' + $id + '. Skipping.'^)
echo  $analysis.summary_file = $staticPath
echo  }
echo }
echo.
echo # Save updated index to both locations (data/web and Flask static^)
echo $json ^| ConvertTo-Json -Depth 10 ^| Set-Content '%INDEX_FILE%'
echo.
echo # Also save to Flask static directory
echo $flaskIndexFile = '%FLASK_INDEX_DIR%\analyses_index.json'
echo $json ^| ConvertTo-Json -Depth 10 ^| Set-Content $flaskIndexFile
) > "%TEMP_PS_SCRIPT%"

:: Run the PowerShell script
echo Running PowerShell script to update index file...
powershell -ExecutionPolicy Bypass -File "%TEMP_PS_SCRIPT%"

:: Clean up temporary file
del "%TEMP_PS_SCRIPT%"

echo.
echo SUCCESS! The analyses_index.json file has been updated with paths for Flask.
echo Summary files have been copied to Flask static directory.
echo.

:: Create the Flask tester HTML file
echo Creating a simple Flask URL tester for debugging...

:: Create a simplified version without problematic template literals
(
echo ^<!DOCTYPE html^>
echo ^<html^>
echo ^<head^>
echo     ^<title^>Flask Path Tester^</title^>
echo     ^<style^>
echo         body { font-family: Arial, sans-serif; margin: 20px; }
echo         .success { color: green; }
echo         .error { color: red; }
echo         .loading { color: blue; }
echo         .file-path { font-family: monospace; background: #f5f5f5; padding: 2px 5px; }
echo     ^</style^>
echo ^</head^>
echo ^<body^>
echo     ^<h1^>Flask Analysis Files Test^</h1^>
echo     
echo     ^<h2^>Index File Test^</h2^>
echo     ^<div id="index-test"^>Testing...^</div^>
echo     
echo     ^<h2^>Summary Files Test^</h2^>
echo     ^<div id="summary-test"^>Will load after index is found...^</div^>
echo     
echo     ^<script^>
echo         // Test index file
echo         async function testIndexFile() {
echo             const testDiv = document.getElementById('index-test');
echo             
echo             try {
echo                 const response = await fetch('/static/data/analyses_index.json');
echo                 
echo                 if (response.ok) {
echo                     const data = await response.json();
echo                     testDiv.innerHTML = '✓ Successfully loaded index file! Found ' + data.analyses.length + ' analyses.';
echo                     return data;
echo                 } else {
echo                     testDiv.innerHTML = '✗ Failed to load index file. Status: ' + response.status;
echo                     return null;
echo                 }
echo             } catch (error) {
echo                 testDiv.innerHTML = '✗ Error loading index file: ' + error.message;
echo                 return null;
echo             }
echo         }
echo         
echo         // Test summary files
echo         async function testSummaryFiles(indexData) {
echo             const testDiv = document.getElementById('summary-test');
echo             
echo             if (!indexData) {
echo                 testDiv.innerHTML = 'Cannot test summary files - index file not loaded';
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
echo                 summaryDiv.innerHTML = 'Testing ' + analysis.analysis_type + '...';
echo                 testDiv.appendChild(summaryDiv);
echo                 
echo                 try {
echo                     const response = await fetch(analysis.summary_file);
echo                     
echo                     if (response.ok) {
echo                         successCount++;
echo                         summaryDiv.innerHTML = '✓ Successfully loaded summary for ' + analysis.analysis_type;
echo                     } else {
echo                         failCount++;
echo                         summaryDiv.innerHTML = '✗ Failed to load summary for ' + analysis.analysis_type + ' (Status: ' + response.status + ')';
echo                     }
echo                 } catch (error) {
echo                     failCount++;
echo                     summaryDiv.innerHTML = '✗ Error loading summary for ' + analysis.analysis_type + ': ' + error.message;
echo                 }
echo             }
echo             
echo             // Add summary
echo             const summaryDiv = document.createElement('div');
echo             summaryDiv.style.marginTop = '20px';
echo             summaryDiv.style.padding = '10px';
echo             summaryDiv.style.background = '#f5f5f5';
echo             
echo             if (failCount === 0) {
echo                 summaryDiv.innerHTML = 'All ' + successCount + ' files loaded successfully!';
echo             } else {
echo                 summaryDiv.innerHTML = 'Loaded: ' + successCount + ' files, Failed: ' + failCount + ' files';
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
) > "%~dp0..\..\src\web\templates\flask_path_tester.html"

echo Created flask_path_tester.html in the templates directory for debugging.
echo.
echo All modifications complete!
echo Now you can run the Flask app by executing start_flask.bat
echo.

pause
