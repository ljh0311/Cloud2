# PowerShell script to generate analyses_index.json from analysis directories

# Get the script's directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataDir = Join-Path -Path $scriptDir -ChildPath ".."
$webDataDir = Join-Path -Path $dataDir -ChildPath "web\visualizations\data"
$indexFile = Join-Path -Path $webDataDir -ChildPath "analyses_index.json"

# Create the web data directory if it doesn't exist
if (-not (Test-Path -Path $webDataDir)) {
    New-Item -Path $webDataDir -ItemType Directory -Force
    Write-Host "Created output directory at $webDataDir"
}

Write-Host "Building analysis index..."
Write-Host ""

# Get all directories in the analysis folder
$analysisDirs = Get-ChildItem -Path $scriptDir -Directory

# Create an array to hold all analyses
$analyses = @()

foreach ($dir in $analysisDirs) {
    $dirName = $dir.Name
    
    # Skip if it doesn't match our expected format
    if ($dirName -match "^list_analyses\.ps1$|^update_index\.bat$") {
        continue
    }
    
    Write-Host "Processing $dirName..."
    
    # Check if part-r-00000 exists (indicates completed analysis)
    $outputFile = Join-Path -Path $dir.FullName -ChildPath "part-r-00000"
    if (Test-Path -Path $outputFile) {
        # Parse directory name to extract components (format: dataset_datadate_rundate_analysis)
        if ($dirName -match "^([^_]+)_([^_]+)_([^_]+)_([^_]+)$") {
            $dataset = $matches[1]
            $dataDate = $matches[2]
            $runDate = $matches[3]
            $analysisType = $matches[4]
            
            # Create the analysis entry
            $analysisEntry = @{
                dataset = "${dataset}_${dataDate}"
                data_date = $dataDate
                run_date = $runDate
                analysis_type = $analysisType
                summary_file = "/static/data/$dirName/summary.json"
                output_dir = "../../data/analysis/$dirName"
            }
            
            $analyses += $analysisEntry
            
            # Create summary JSON file if it doesn't exist
            $summaryDir = Join-Path -Path $webDataDir -ChildPath $dirName
            $summaryFile = Join-Path -Path $summaryDir -ChildPath "summary.json"
            
            if (-not (Test-Path -Path $summaryDir)) {
                New-Item -Path $summaryDir -ItemType Directory -Force
                Write-Host "Created summary directory at $summaryDir"
            }
            
            if (-not (Test-Path -Path $summaryFile)) {
                Write-Host "Creating summary file for $dirName..."
                $summaryContent = @{
                    dataset = "${dataset}_${dataDate}"
                    data_date = $dataDate
                    run_date = $runDate
                    analysis_type = $analysisType
                    output_dir = "../../data/analysis/$dirName"
                }
                
                $summaryContent | ConvertTo-Json -Depth 10 | Out-File -FilePath $summaryFile -Encoding utf8
            }
        }
        else {
            Write-Host "  Warning: Directory name format not recognized. Expected format: dataset_datadate_rundate_analysis"
        }
    }
    else {
        Write-Host "  Skipped $dirName - no analysis output found"
    }
}

# Create the final JSON with all analyses
$indexJson = @{
    analyses = $analyses
} | ConvertTo-Json -Depth 10

# Save to file
$indexJson | Out-File -FilePath $indexFile -Encoding utf8

Write-Host ""
Write-Host "Analysis index complete at $indexFile"
Write-Host ""

# Display the found analyses
Write-Host "Found $($analyses.Count) analyses:"
foreach ($analysis in $analyses) {
    Write-Host "- $($analysis.dataset) ($($analysis.analysis_type)) from $($analysis.run_date)"
}

Write-Host ""
Write-Host "Press any key to exit..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 