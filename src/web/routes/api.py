from flask import Blueprint, jsonify, current_app, request, send_file
import os
import json
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import subprocess
import threading
import time
import logging

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

# Add a new route for running Hadoop jobs
@api.route('/run_hadoop_job', methods=['POST'])
def run_hadoop_job():
    """
    Run a Hadoop job with specified parameters
    
    Expected JSON payload:
    {
        "input_file": "/path/to/input.json",
        "analysis_type": "sentiment|traffic|location|brands|trend",
        "output_dir": "/path/to/output",
        "timerange_start": "YYYY-MM-DDTHH:MM" (optional),
        "timerange_end": "YYYY-MM-DDTHH:MM" (optional)
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'input_file' not in data or 'analysis_type' not in data or 'output_dir' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: input_file, analysis_type, or output_dir'
            }), 400
        
        # Validate analysis type
        valid_analysis_types = ['sentiment', 'traffic', 'location', 'brands', 'trend']
        if data['analysis_type'] not in valid_analysis_types:
            return jsonify({
                'status': 'error',
                'message': f'Invalid analysis type. Must be one of: {", ".join(valid_analysis_types)}'
            }), 400
        
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Get parameters
        input_file = data['input_file']
        analysis_type = data['analysis_type']
        output_dir = data['output_dir']
        timerange_start = data.get('timerange_start', '')
        timerange_end = data.get('timerange_end', '')
        
        # Create timestamp string for output directory naming
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = os.path.basename(input_file).split('.')[0]
        
        # Format the output directory with dataset and timestamp
        # This will create a directory like: output_dir/dataset_name_analysis_type_timestamp
        formatted_output_dir = os.path.join(
            output_dir,
            f"{dataset_name}_{analysis_type}_{timestamp}"
        )
        
        # Determine the JAR file to use
        jar_mapping = {
            'sentiment': 'TAsentiment.jar',
            'traffic': 'TAtraffic.jar',
            'location': 'TAlocation.jar',
            'brands': 'TAbrands.jar',
            'trend': 'TAtrend.jar'
        }
        
        jar_file = jar_mapping[analysis_type]
        
        # Get the project root directory (3 levels up from routes)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Construct the hadoop jar command
        hadoop_jar_path = os.path.join(project_root, 'HadoopJar', jar_file)
        
        # Build the command
        cmd = [
            'hadoop', 'jar', hadoop_jar_path,
            input_file,
            analysis_type,
            formatted_output_dir
        ]
        
        # Add timestamp parameters if provided
        if timerange_start:
            cmd.append('--start-time')
            cmd.append(timerange_start.replace('T', ' '))
        
        if timerange_end:
            cmd.append('--end-time')
            cmd.append(timerange_end.replace('T', ' '))
        
        # Log the command
        logging.info(f"Running Hadoop job: {' '.join(cmd)}")
        
        # Store job info
        job_info = {
            'id': job_id,
            'input_file': input_file,
            'analysis_type': analysis_type,
            'output_dir': formatted_output_dir,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'cmd': ' '.join(cmd)
        }
        
        # Start job in background thread
        thread = threading.Thread(
            target=run_hadoop_job_thread,
            args=(job_id, cmd, job_info)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Job submitted successfully',
            'job_id': job_id,
            'output_dir': formatted_output_dir
        })
        
    except Exception as e:
        logging.error(f"Error running Hadoop job: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error running Hadoop job: {str(e)}'
        }), 500

def run_hadoop_job_thread(job_id, cmd, job_info):
    """Run the Hadoop job in a background thread"""
    try:
        # Store active jobs in a global dictionary (could be replaced with a database)
        if not hasattr(current_app, 'active_jobs'):
            current_app.active_jobs = {}
        
        current_app.active_jobs[job_id] = job_info
        
        # Create the output directory if it doesn't exist
        os.makedirs(job_info['output_dir'], exist_ok=True)
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Capture output in real-time
        stdout, stderr = process.communicate()
        
        # Update job info
        job_info['end_time'] = datetime.now().isoformat()
        job_info['exit_code'] = process.returncode
        
        if process.returncode == 0:
            job_info['status'] = 'completed'
            
            # Process the output to generate visualization files
            process_hadoop_output(job_info)
        else:
            job_info['status'] = 'failed'
            job_info['error'] = stderr
        
        # Update the stored job info
        current_app.active_jobs[job_id] = job_info
        
    except Exception as e:
        logging.error(f"Error in Hadoop job thread: {str(e)}")
        
        # Update job info with error
        if job_id in current_app.active_jobs:
            current_app.active_jobs[job_id]['status'] = 'failed'
            current_app.active_jobs[job_id]['error'] = str(e)

def process_hadoop_output(job_info):
    """
    Process Hadoop job output to generate visualization files
    This function would:
    1. Read the output from the Hadoop job
    2. Generate a summary.json file for visualization
    3. Update the analyses_index.json file
    """
    try:
        # Get paths
        output_dir = job_info['output_dir']
        analysis_type = job_info['analysis_type']
        dataset_name = os.path.basename(job_info['input_file']).split('.')[0]
        
        # Create visualization directory
        viz_dir = os.path.join(output_dir, 'visualization')
        os.makedirs(viz_dir, exist_ok=True)
        
        # Read Hadoop output
        part_files = []
        for file_name in os.listdir(output_dir):
            if file_name.startswith('part-r-'):
                part_files.append(os.path.join(output_dir, file_name))
        
        # Combine output from part files
        combined_data = []
        for part_file in part_files:
            with open(part_file, 'r') as f:
                for line in f:
                    # Hadoop output is typically tab-separated
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        combined_data.append({
                            'key': parts[0],
                            'value': int(parts[1]) if parts[1].isdigit() else parts[1]
                        })
        
        # Create summary JSON
        summary = {
            'dataset_id': dataset_name,
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'data': combined_data
        }
        
        # Write summary to file
        summary_file = os.path.join(viz_dir, 'summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Update the analyses index file
        update_analyses_index(job_info, summary_file)
        
    except Exception as e:
        logging.error(f"Error processing Hadoop output: {str(e)}")

def update_analyses_index(job_info, summary_file):
    """Update the analyses_index.json file with the new analysis"""
    try:
        # Get paths
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, 'data')
        web_dir = os.path.join(data_dir, 'web')
        viz_data_dir = os.path.join(web_dir, 'visualizations', 'data')
        index_file = os.path.join(viz_data_dir, 'analyses_index.json')
        
        # Create directories if they don't exist
        os.makedirs(viz_data_dir, exist_ok=True)
        
        # Load existing index file or create new one
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
        else:
            index_data = {
                'last_updated': datetime.now().isoformat(),
                'analyses': []
            }
        
        # Extract information from job info
        dataset_name = os.path.basename(job_info['input_file']).split('.')[0]
        analysis_type = job_info['analysis_type']
        output_dir = job_info['output_dir']
        
        # Determine ID for this analysis
        # Format: dataset_analysis-type_timestamp
        run_date = os.path.basename(output_dir).split('_')[-1]
        analysis_id = os.path.basename(output_dir)
        
        # Create relative path for summary file
        # Use a path relative to the web root for Flask to serve
        rel_summary_path = f'/static/data/{analysis_id}.json'
        
        # Create new analysis entry
        new_analysis = {
            'id': analysis_id,
            'dataset': dataset_name,
            'analysis_type': analysis_type,
            'run_date': run_date,
            'data_date': datetime.now().strftime('%Y-%m-%d'),
            'summary_file': rel_summary_path
        }
        
        # Add to analyses list
        index_data['analyses'].append(new_analysis)
        index_data['last_updated'] = datetime.now().isoformat()
        
        # Write updated index back to file
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        # Copy summary file to Flask static directory
        flask_static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'data')
        os.makedirs(flask_static_dir, exist_ok=True)
        
        flask_summary_file = os.path.join(flask_static_dir, f'{analysis_id}.json')
        
        # Copy the file
        with open(summary_file, 'r') as src, open(flask_summary_file, 'w') as dst:
            dst.write(src.read())
        
        # Also copy the index file
        flask_index_file = os.path.join(flask_static_dir, 'analyses_index.json')
        with open(index_file, 'r') as src, open(flask_index_file, 'w') as dst:
            dst.write(src.read())
        
        logging.info(f"Successfully updated analyses index with {analysis_id}")
        
    except Exception as e:
        logging.error(f"Error updating analyses index: {str(e)}")

@api.route('/job_status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a running Hadoop job"""
    try:
        # Check if we have the job in our active jobs
        if not hasattr(current_app, 'active_jobs') or job_id not in current_app.active_jobs:
            return jsonify({
                'status': 'error',
                'message': 'Job not found'
            }), 404
        
        # Return the job info
        job_info = current_app.active_jobs[job_id]
        return jsonify({
            'status': 'success',
            'job': job_info
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting job status: {str(e)}'
        }), 500

@api.route('/browse_directory', methods=['GET'])
def browse_directory():
    """API endpoint to browse directories for the output path selection"""
    try:
        # This is a simplified version that would need to be expanded
        # In a real implementation, you'd have more sophisticated directory browsing
        
        # For security reasons, limit to specific directories
        allowed_base_dirs = [
            os.path.join(os.getcwd(), 'output'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'analysis')
        ]
        
        # Default to the data/analysis directory
        default_dir = allowed_base_dirs[1]
        
        return jsonify({
            'status': 'success',
            'path': default_dir
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error browsing directory: {str(e)}'
        }), 500 