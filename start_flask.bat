@echo off
echo Starting Flask application for traffic analysis visualization...
echo.
echo This will run the Flask app from the root directory
echo Open your browser and go to: http://localhost:5000/visualizations
echo or http://localhost:5000/flask_path_test for testing paths
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the fix_index_paths.bat script first to ensure all files are properly set up
echo Running fix_index_paths.bat to prepare data files...
cd data\web
call fix_index_paths.bat

REM Navigate back to the root directory
cd ..\..

REM Run the Flask application
echo Starting Flask app in directory: %CD%
python app.py

pause