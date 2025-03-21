# Analysis Files Management

This document provides information about how analysis files are managed in the Social Media Analyzer application.

## Analysis Files Location

Analysis files are stored in the `data/analysis` directory by default. This location is configured in the `AnalysisService` class in `src/web/services.py`.

## How Analysis Files Are Saved

1. When you analyze Reddit data using the "Analyze Data" button on the Analysis page, the application:
   - Processes the Reddit data using the `process_reddit_data` method in `AnalysisService`
   - Generates analysis results for sentiment, trends, engagement, and topics
   - Saves the results to a JSON file in the `data/analysis` directory
   - The filename is generated based on the dataset name and a timestamp

2. The API endpoint `/api/analyze-reddit-data` in `src/web/views.py` handles the request and calls the `process_reddit_data` method.

3. The `save_analysis_results` method in `AnalysisService` handles the actual saving of the file.

## Ensuring Analysis Files Are Saved Correctly

To ensure that analysis files are saved to the correct location:

1. **Check the directory structure**: Make sure the `data/analysis` directory exists. The application will create it if it doesn't exist, but it's good to verify.

2. **Check file permissions**: Ensure that the application has write permissions to the `data/analysis` directory.

3. **Verify the analysis service initialization**: The `AnalysisService` is initialized in `src/web/views.py` with the default analysis directory path.

4. **Check the logs**: The application logs information about where files are being saved. Look for log messages like:
   ```
   Saving analysis results to: data/analysis/reddit_technology_1742189496.json
   Analysis results saved successfully to: data/analysis/reddit_technology_1742189496.json
   ```

5. **Run the test script**: You can run the `test_analysis_save.py` script to verify that analysis files are being saved correctly:
   ```
   python test_analysis_save.py
   ```

## Troubleshooting

If analysis files are not being saved correctly:

1. **Check the logs**: Look for error messages in the logs.

2. **Check the directory structure**: Make sure the `data/analysis` directory exists and has the correct permissions.

3. **Check the file path**: Make sure the file path is correct and the application has permission to write to it.

4. **Check the API response**: The API response includes the file path where the analysis was saved. Check this path to see if it's correct.

5. **Run the test script**: The `test_analysis_save.py` script can help diagnose issues with saving analysis files.

## Customizing the Analysis Files Location

If you want to change the location where analysis files are saved:

1. Modify the `AnalysisService` initialization in `src/web/views.py`:
   ```python
   analysis_service = AnalysisService(analysis_dir="your/custom/path")
   ```

2. Make sure the new directory exists and has the correct permissions.

3. Update any references to the analysis directory in your code.

## Viewing Analysis Files

Analysis files can be viewed in the Visualizations page of the application. The application reads the analysis files from the `data/analysis` directory and displays them in the dropdown menu.

You can also view the raw JSON files directly by opening them in a text editor or JSON viewer. 