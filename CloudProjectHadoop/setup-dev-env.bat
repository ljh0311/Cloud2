@echo off
echo Setting up development environment for Hadoop Traffic Analysis...

REM Set HADOOP_HOME if set-hadoop-env.bat exists
if exist set-hadoop-env.bat (
  call set-hadoop-env.bat
) else (
  echo WARNING: set-hadoop-env.bat not found. HADOOP_HOME may not be set correctly.
  echo Run install-hadoop-windows.bat first to set up Hadoop for Windows.
)

REM Create testdata directory if it doesn't exist
if not exist testdata mkdir testdata
echo Created testdata directory: %CD%\testdata

REM Create sample test data if it doesn't exist
if not exist testdata\sample_traffic_data.json (
  echo Creating sample test data...
  echo { "text": "Heavy traffic jam on PIE near Jurong exit. #sgtraffic" } > testdata\sample_traffic_data.json
  echo { "text": "Accident on CTE causing delays. Drive safely! #sgtraffic" } >> testdata\sample_traffic_data.json
  echo { "text": "Smooth traffic along ECP this morning. What a pleasant drive! #sgtraffic" } >> testdata\sample_traffic_data.json
  echo Sample data created at: %CD%\testdata\sample_traffic_data.json
) else (
  echo Sample data already exists at: %CD%\testdata\sample_traffic_data.json
)

REM Make sure Python scripts are in the working directory
echo Copying Python scripts to working directory...
copy /Y %~dp0mapper.py .
echo Copied mapper.py to: %CD%\mapper.py
copy /Y %~dp0reducer.py .
echo Copied reducer.py to: %CD%\reducer.py

REM Create output directory
if not exist output mkdir output
echo Created output directory: %CD%\output

REM Clean previous output
if exist output\sentiment_results rmdir /S /Q output\sentiment_results
if exist output\trend_results rmdir /S /Q output\trend_results
if exist output\traffic_results rmdir /S /Q output\traffic_results
if exist output\location_results rmdir /S /Q output\location_results
if exist output\topic_results rmdir /S /Q output\topic_results
if exist output\engagement_results rmdir /S /Q output\engagement_results
echo Cleaned previous output directories

REM Copy properties file to working directory if it's not already there
if not exist traffic-analysis.properties (
  if exist src\main\resources\traffic-analysis.properties (
    copy /Y src\main\resources\traffic-analysis.properties .
    echo Copied properties file to: %CD%\traffic-analysis.properties
  )
)

echo.
echo Development environment setup complete!
echo.
echo CURRENT WORKING DIRECTORY: %CD%
echo HADOOP_HOME: %HADOOP_HOME%
echo.
echo You can now run your Hadoop jobs from Eclipse with the following sample commands:
echo.
echo java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job sentiment -input testdata/sample_traffic_data.json -output output/sentiment_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive
echo.
echo java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job trend -input testdata/sample_traffic_data.json -output output/trend_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive
echo. 