# List all analysis directories and generate a JSON index file
$analysisDir = $PSScriptRoot
$outputDir = "$analysisDir\..\web\visualizations\data"
$outputFile = "$outputDir\analyses_index.json"

Write-Host "Analysis directory: $analysisDir"
Write-Host "Output directory: $outputDir"
Write-Host "Output file: $outputFile"

# Create output directory if it doesn't exist (create all parent directories)
if (-not (Test-Path $outputDir)) {
    Write-Host "Creating output directory: $outputDir"
    New-Item -ItemType Directory -Path $outputDir -Force
}

# Get all directories that match our naming pattern
$analysisFolders = Get-ChildItem -Path $analysisDir -Directory | Where-Object {
    $_.Name -match "^[a-zA-Z0-9_]+_\d+_\d+_[a-zA-Z0-9_]+_\d+_\d+" -or 
    $_.Name -match "^[a-zA-Z0-9_]+"  # Also include simpler named folders
}

Write-Host "Found $($analysisFolders.Count) matching directories"

# Parse directory names and check for summary.json files
$analyses = @()
foreach ($folder in $analysisFolders) {
    # Check for visualization/summary.json or just summary.json
    $summaryFiles = @(
        (Join-Path $folder.FullName "visualization\summary.json"),
        (Join-Path $folder.FullName "summary.json")
    )
    
    $summaryFile = $summaryFiles | Where-Object { Test-Path $_ } | Select-Object -First 1
    
    if ($summaryFile) {
        Write-Host "Found summary file in: $($folder.Name)"
        
        # Try to extract components from folder name or use generic values
        if ($folder.Name -match "^(.+?)_(\d+)_(\d+)_(.+?)_(\d+)_(\d+)") {
            $dataset = $matches[1]
            $dataDate = "$($matches[2])_$($matches[3])"
            $analysisType = $matches[4]
            $runDate = "$($matches[5])_$($matches[6])"
        } else {
            # For simpler named folders
            $dataset = $folder.Name
            $dataDate = Get-Date -Format "yyyyMMdd"
            $analysisType = "unknown"
            $runDate = Get-Date -Format "yyyyMMdd_HHmmss"
        }
        
        # Get the relative path from the analysis dir
        $relPath = $summaryFile.Replace($analysisDir, "").TrimStart("\")
        
        $analyses += @{
            "id" = $folder.Name
            "dataset" = "$dataset"
            "data_date" = $dataDate
            "analysis_type" = $analysisType
            "run_date" = $runDate
            "summary_file" = $relPath
            "display_name" = "$analysisType analysis of $dataset ($runDate)"
        }
    } else {
        Write-Host "No summary file found in: $($folder.Name)"
    }
}

# Create the final JSON
$result = @{
    "analyses" = $analyses
    "timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "count" = $analyses.Count
}

# Save to JSON file
Write-Host "Writing output file: $outputFile"
$result | ConvertTo-Json -Depth 10 | Set-Content $outputFile

Write-Host "Found $($analyses.Count) analysis directories"
Write-Host "Generated index file: $outputFile"

# Return JSON to console for direct API use
$result | ConvertTo-Json -Depth 10 