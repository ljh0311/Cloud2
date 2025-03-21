from flask import Blueprint, jsonify, current_app, request, send_file
import os
import json
import csv
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/datasets', methods=['GET'])
def get_datasets():
    try:
        datasets = []
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        data_dir = os.path.join(base_dir, 'data')
        
        print(f"Looking for datasets in: {data_dir}")
        
        # Reddit datasets
        reddit_dir = os.path.join(data_dir, 'reddit')
        if os.path.exists(reddit_dir):
            print(f"Found Reddit directory: {reddit_dir}")
            for file in os.listdir(reddit_dir):
                if file.endswith(('.json', '.csv')):
                    file_path = os.path.join(reddit_dir, file)
                    print(f"Processing Reddit file: {file_path}")
                    dataset = get_dataset_info('reddit', file, file_path)
                    if dataset:
                        datasets.append(dataset)
        else:
            print(f"Reddit directory not found at: {reddit_dir}")
        
        # Twitter datasets
        twitter_dir = os.path.join(data_dir, 'twitter')
        if os.path.exists(twitter_dir):
            print(f"Found Twitter directory: {twitter_dir}")
            for file in os.listdir(twitter_dir):
                if file.endswith(('.json', '.csv')):
                    file_path = os.path.join(twitter_dir, file)
                    print(f"Processing Twitter file: {file_path}")
                    dataset = get_dataset_info('twitter', file, file_path)
                    if dataset:
                        datasets.append(dataset)
        else:
            print(f"Twitter directory not found at: {twitter_dir}")
        
        # Sort datasets by date (newest first)
        sorted_datasets = sorted(datasets, key=lambda x: x['date'], reverse=True)
        
        print(f"Total datasets found: {len(sorted_datasets)}")
        
        return jsonify({
            'success': True,
            'datasets': sorted_datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_datasets: {str(e)}")
        print(f"Error occurred: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load datasets',
            'message': str(e)
        }), 500

def get_dataset_info(source, filename, file_path):
    try:
        # Get file stats
        stats = os.stat(file_path)
        size = stats.st_size
        modified_date = datetime.fromtimestamp(stats.st_mtime)
        
        # Extract date range from filename if available
        date_range = None
        if '_20' in filename:
            parts = filename.split('_')
            for part in parts:
                if part.startswith('20'):
                    date_range = part.split('.')[0]
        elif '_17' in filename:  # For Unix timestamp filenames
            parts = filename.split('_')
            for part in parts:
                if part.startswith('17'):
                    try:
                        timestamp = int(part.split('.')[0])
                        date = datetime.fromtimestamp(timestamp)
                        date_range = date.strftime('%Y%m%d')
                    except:
                        pass
        
        # Get item count from file
        item_count = 0
        file_ext = os.path.splitext(filename)[1].lower()
        
        try:
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        item_count = len(data)
                    elif isinstance(data, dict) and 'data' in data:
                        item_count = len(data['data'])
            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    # Subtract 1 to account for header row
                    item_count = sum(1 for row in csv_reader) - 1
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
            current_app.logger.warning(f"Error reading file {filename}: {str(e)}")
        
        # Format size for display
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"
        
        # Format name for display
        display_name = os.path.splitext(filename)[0].replace('_', ' ').title()
        
        # Add file type indicator to name
        file_type = 'JSON' if file_ext == '.json' else 'CSV'
        display_name = f"{display_name} ({file_type})"
        
        # Create a server-relative path for the dataset
        # This transforms absolute file paths into routes for the Flask server
        relative_path = '/data/' + source + '/' + filename
        
        dataset_info = {
            'id': os.path.splitext(filename)[0],
            'name': display_name,
            'source': source,
            'path': relative_path,
            'size': size_str,
            'item_count': item_count,
            'date_range': date_range,
            'date': modified_date.strftime('%Y-%m-%d %H:%M:%S'),
            'type': file_type.lower()
        }
        print(f"Processed dataset: {dataset_info}")
        return dataset_info
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        current_app.logger.error(f"Error processing {filename}: {str(e)}")
        return None

@api.route('/analyze', methods=['POST'])
def analyze_dataset():
    # Your existing analysis endpoint code here
    return jsonify({
        'success': True,
        'message': 'Analysis started'
    }) 

@api.route('/get-analysis-files', methods=['GET'])
def get_analysis_files():
    """API endpoint to get available analysis files"""
    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        analysis_dir = os.path.join(base_dir, 'data', 'analysis')
        
        print(f"Looking for analysis files in: {analysis_dir}")
        
        files = []
        
        if os.path.exists(analysis_dir):
            for filename in os.listdir(analysis_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(analysis_dir, filename)
                    stats = os.stat(file_path)
                    
                    # Format size for display
                    size = stats.st_size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    
                    # Get date from the file modification time
                    modified_date = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Create a formatted display name
                    display_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    
                    # Create a relative path for the file
                    relative_path = '/data/analysis/' + filename
                    
                    files.append({
                        'filename': display_name,
                        'size': size_str,
                        'date': modified_date,
                        'path': relative_path,
                        'raw_filename': filename
                    })
            
            # Sort files by creation time (newest first)
            files = sorted(files, key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'files': files
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_analysis_files: {str(e)}")
        print(f"Error occurred while getting analysis files: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load analysis files',
            'error': str(e)
        }), 500

@api.route('/get-visualizations', methods=['GET'])
def get_visualizations():
    """API endpoint to get visualization data for an analysis"""
    try:
        file_path = request.args.get('file')
        viz_type = request.args.get('type', 'all')
        timeframe = request.args.get('timeframe', '30d')
        
        # Get the absolute path to the file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        # Handle case where the file path is relative to the server
        if file_path.startswith('/data/'):
            file_path = file_path.replace('/data/', '', 1)
            file_path = os.path.join(base_dir, 'data', file_path)
        
        print(f"Loading visualizations from: {file_path}")
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': f"Analysis file not found: {file_path}"
            })
        
        # Read the analysis file
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Filter data based on visualization type if needed
        if viz_type != 'all':
            filtered_data = {}
            for key, value in analysis_data.items():
                if key.startswith(viz_type):
                    filtered_data[key] = value
            analysis_data = filtered_data
        
        # Apply timeframe filtering if applicable
        # This would be applied to any time series data in the analysis
        
        return jsonify({
            'status': 'success',
            'data': analysis_data
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_visualizations: {str(e)}")
        print(f"Error occurred while getting visualizations: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load visualizations',
            'error': str(e)
        }), 500 