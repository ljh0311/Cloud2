@echo off
echo Setting up Hadoop for Windows development...

REM Create hadoop directory structure if it doesn't exist
if not exist hadoop-windows mkdir hadoop-windows
cd hadoop-windows

echo Downloading Hadoop Windows Binaries...
REM Using PowerShell to download files
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe', 'winutils.exe')"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/hadoop.dll', 'hadoop.dll')"

if exist winutils.exe (
    echo Successfully downloaded Hadoop Windows binaries.
) else (
    echo Failed to download Hadoop Windows binaries.
    echo Please download manually from https://github.com/steveloughran/winutils
    echo and place in the hadoop-windows directory.
)

REM Create bin directory for Hadoop
if not exist bin mkdir bin
move /Y winutils.exe bin\
move /Y hadoop.dll bin\

cd ..

REM Set HADOOP_HOME environment variable for the current session
set HADOOP_HOME=%CD%\hadoop-windows
echo Set HADOOP_HOME to %HADOOP_HOME%

REM Create a batch file to set HADOOP_HOME for Eclipse
echo @echo off > set-hadoop-env.bat
echo set HADOOP_HOME=%CD%\hadoop-windows >> set-hadoop-env.bat
echo echo HADOOP_HOME set to %%HADOOP_HOME%% >> set-hadoop-env.bat

echo.
echo ===========================================================================
echo INSTRUCTIONS:
echo ===========================================================================
echo 1. Add the following system environment variable (requires admin privileges):
echo.
echo    Variable: HADOOP_HOME
echo    Value: %CD%\hadoop-windows
echo.
echo 2. In Eclipse, go to:
echo    Run -^> Run Configurations -^> Environment -^> Add...
echo    Add HADOOP_HOME with value: %CD%\hadoop-windows
echo.
echo 3. Before running your Hadoop job, execute:
echo    set-hadoop-env.bat
echo.
echo ===========================================================================
echo. 