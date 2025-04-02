@echo off
echo Running all traffic analysis job types...

REM Run setup first to ensure environment is ready
call setup-dev-env.bat

REM Run each job type
echo.
echo === Running Sentiment Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job sentiment -input testdata\sample_traffic_data.json -output output\sentiment_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo === Running Trend Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job trend -input testdata\sample_traffic_data.json -output output\trend_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo === Running Traffic Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job traffic -input testdata\sample_traffic_data.json -output output\traffic_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo === Running Location Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job location -input testdata\sample_traffic_data.json -output output\location_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo === Running Topic Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job topic -input testdata\sample_traffic_data.json -output output\topic_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo === Running Engagement Analysis ===
echo.
java -cp target\classes;target\dependency\* sg.edu.sit.traffic.TrafficAnalysisDriver -job engagement -input testdata\sample_traffic_data.json -output output\engagement_results -mapper mapper.py -reducer reducer.py -depth advanced -visual interactive

echo.
echo All jobs completed!
echo Results are available in the output directory. 