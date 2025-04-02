# PowerShell script to set up Hadoop for Windows development
Write-Host "Setting up Hadoop for Windows development..."

# Create hadoop directory structure if it doesn't exist
$hadoopDir = "hadoop-windows"
if (-not (Test-Path $hadoopDir)) {
    New-Item -ItemType Directory -Path $hadoopDir | Out-Null
}

Set-Location $hadoopDir

Write-Host "Downloading Hadoop Windows Binaries..."
# Download winutils.exe and hadoop.dll
$winutilsUrl = "https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe"
$hadoopDllUrl = "https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/hadoop.dll"

try {
    Invoke-WebRequest -Uri $winutilsUrl -OutFile "winutils.exe"
    Invoke-WebRequest -Uri $hadoopDllUrl -OutFile "hadoop.dll"
    Write-Host "Successfully downloaded Hadoop Windows binaries."
} catch {
    Write-Host "Failed to download Hadoop Windows binaries."
    Write-Host "Please download manually from https://github.com/steveloughran/winutils"
    Write-Host "and place in the hadoop-windows directory."
}

# Create bin directory for Hadoop
if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

# Move files to bin directory
Move-Item -Path "winutils.exe" -Destination "bin\" -Force
Move-Item -Path "hadoop.dll" -Destination "bin\" -Force

Set-Location ..

# Set HADOOP_HOME environment variable for the current session
$hadoopHome = Join-Path $PWD.Path "hadoop-windows"
$env:HADOOP_HOME = $hadoopHome
Write-Host "Set HADOOP_HOME to $hadoopHome"

# Create a batch file to set HADOOP_HOME for Eclipse
@"
@echo off
set HADOOP_HOME=$hadoopHome
echo HADOOP_HOME set to %HADOOP_HOME%
"@ | Out-File -FilePath "set-hadoop-env.bat" -Encoding ASCII

Write-Host "`n==========================================================================="
Write-Host "INSTRUCTIONS:"
Write-Host "==========================================================================="
Write-Host "1. Add the following system environment variable (requires admin privileges):`n"
Write-Host "   Variable: HADOOP_HOME"
Write-Host "   Value: $hadoopHome`n"
Write-Host "2. In Eclipse, go to:"
Write-Host "   Run -> Run Configurations -> Environment -> Add..."
Write-Host "   Add HADOOP_HOME with value: $hadoopHome`n"
Write-Host "3. Before running your Hadoop job, execute:"
Write-Host "   set-hadoop-env.bat`n"
Write-Host "==========================================================================="`n 