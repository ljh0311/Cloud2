"""
Progress tracking utility for Big Data Analytics project
"""
import os
import json
from pathlib import Path
from datetime import datetime

class ProjectProgressTracker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.required_components = {
            'Data Storage': [
                'src/storage/hdfs_manager.py',
                'src/storage/data_loader.py'
            ],
            'Data Processing': [
                'src/processing/mapreduce_jobs.py',
                'src/processing/data_cleaner.py'
            ],
            'Spark Analysis': [
                'src/spark/spark_analysis.py',
                'src/spark/streaming.py'
            ],
            'Visualization': [
                'src/web/templates/visualizations.html',
                'src/web/static/js/charts.js'
            ],
            'Web Interface': [
                'src/web/app.py',
                'src/web/templates/base.html',
                'src/web/templates/index.html'
            ]
        }
        
    def check_file_existence(self, filepath):
        """Check if a file exists in the project"""
        full_path = self.project_root / filepath
        return full_path.exists()
    
    def calculate_component_progress(self, component_files):
        """Calculate progress percentage for a component based on file existence"""
        if not component_files:
            return 0
        
        existing_files = sum(1 for file in component_files if self.check_file_existence(file))
        return (existing_files / len(component_files)) * 100
    
    def get_overall_progress(self):
        """Calculate overall project progress"""
        component_percentages = []
        for component, files in self.required_components.items():
            progress = self.calculate_component_progress(files)
            component_percentages.append(progress)
        
        return sum(component_percentages) / len(component_percentages)
    
    def generate_progress_report(self):
        """Generate a detailed progress report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_progress': self.get_overall_progress(),
            'components': {}
        }
        
        for component, files in self.required_components.items():
            component_progress = self.calculate_component_progress(files)
            report['components'][component] = {
                'progress': component_progress,
                'files': {
                    file: self.check_file_existence(file)
                    for file in files
                }
            }
        
        return report
    
    def save_progress_report(self, output_file='progress_report.json'):
        """Save progress report to a JSON file"""
        report = self.generate_progress_report()
        output_path = self.project_root / 'data' / output_file
        
        # Ensure data directory exists
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path 