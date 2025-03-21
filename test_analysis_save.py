import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the AnalysisService
from src.web.services import AnalysisService

def test_save_analysis():
    """Test that analysis files are saved to the correct location"""
    print("Testing analysis file saving...")
    
    # Create an instance of AnalysisService
    analysis_service = AnalysisService()
    
    # Print the analysis directory
    print(f"Analysis directory: {analysis_service.analysis_dir}")
    
    # Check if the directory exists
    if not os.path.exists(analysis_service.analysis_dir):
        print(f"Creating directory: {analysis_service.analysis_dir}")
        os.makedirs(analysis_service.analysis_dir, exist_ok=True)
    
    # List existing analysis files
    print("\nExisting analysis files:")
    existing_files = []
    if os.path.exists(analysis_service.analysis_dir):
        for filename in os.listdir(analysis_service.analysis_dir):
            if filename.endswith('.json'):
                existing_files.append(filename)
                print(f"  - {filename}")
    
    if not existing_files:
        print("  No existing analysis files found.")
    
    # Create a sample analysis data
    test_analysis = {
        "dataset": "Test Analysis",
        "source_file": "test_data.csv",
        "record_count": 10,
        "date_range": "2025-03-10 to 2025-03-17",
        "processing_mode": "batch",
        "analysis_types": ["sentiment", "trend"],
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "results": {
            "sentiment_analysis": {
                "positive_count": 5,
                "neutral_count": 3,
                "negative_count": 2
            },
            "trend_analysis": {
                "time_periods": ["2025-03-10", "2025-03-11"],
                "mention_counts": [5, 5]
            }
        }
    }
    
    # Save the analysis
    print("\nSaving test analysis...")
    result = analysis_service.save_analysis_results(test_analysis)
    
    if result["success"]:
        print(f"Analysis saved successfully!")
        print(f"Analysis ID: {result['analysis_id']}")
        print(f"File path: {result['file_path']}")
        
        # Verify the file exists
        if os.path.exists(result['file_path']):
            print(f"Verified: File exists at the specified path.")
            
            # Read the file to verify content
            with open(result['file_path'], 'r') as f:
                saved_data = json.load(f)
                
            if saved_data["dataset"] == test_analysis["dataset"]:
                print("Verified: File content matches the test data.")
            else:
                print("Error: File content does not match the test data.")
        else:
            print(f"Error: File does not exist at the specified path.")
    else:
        print(f"Error saving analysis: {result['message']}")
    
    # List analysis files again to verify the new file was added
    print("\nUpdated analysis files:")
    if os.path.exists(analysis_service.analysis_dir):
        for filename in os.listdir(analysis_service.analysis_dir):
            if filename.endswith('.json'):
                print(f"  - {filename}")

if __name__ == "__main__":
    test_save_analysis() 