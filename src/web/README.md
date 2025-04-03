# Singapore Traffic Analysis Dashboard

This web dashboard visualizes the results of traffic analysis in Singapore.

## Setup and Usage Instructions

### 1. Generate the Analysis Index

First, you need to generate an index of all available analyses:

1. Open a Command Prompt and navigate to the `data/analysis` directory
2. Run the `update_index.bat` script:
   ```
   cd data\analysis
   update_index.bat
   ```
3. This script will scan all analysis folders and create an index file at `data/web/visualizations/data/analyses_index.json`

### 2. Start the Web Server

To view the dashboard, you need to start a simple web server:

1. Navigate to the project's `src/web` directory
2. Run the `start_web_server.bat` script:
   ```
   cd src\web
   start_web_server.bat
   ```
3. The script will start a Python HTTP server on port 8000

### 3. Access the Dashboard

Once the server is running, open your web browser and go to:
- [http://localhost:8000/src/web/templates/simple_visualizations.html](http://localhost:8000/src/web/templates/simple_visualizations.html)

### 4. Using the Dashboard

- Select a dataset from the dropdown menu to visualize that analysis
- Use the Analysis Type selector to focus on specific aspects of the data
- Click "Refresh Data" to reload the dataset list if you've added new analyses

### 5. Troubleshooting

If you encounter errors:

1. Verify that the `analyses_index.json` file exists in `data/web/visualizations/data/`
2. Check the browser console for specific error messages
3. Try running the test tool at [http://localhost:8000/data/web/test_paths.html](http://localhost:8000/data/web/test_paths.html) to diagnose path issues
4. Ensure all analysis folders have a `visualization/summary.json` or `summary.json` file

## Directory Structure

- `src/web/templates/` - Contains HTML templates for visualization
- `src/web/data/` - Local data storage for web visualizations
- `data/analysis/` - Hadoop analysis results
- `data/web/visualizations/data/` - Index and combined data for visualization

## Available Batch Files

- `update_index.bat` - Creates the analyses index
- `start_web_server.bat` - Starts the web server
- `copy_results.bat` - Copies analysis results to the web data directory (optional) 