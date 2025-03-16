"""
Views for the web application
"""

from flask import Blueprint, render_template, jsonify, request, send_file
from .services import SparkService, VisualizationService, DatasetService
import os
from datetime import datetime, timedelta
import random

main_bp = Blueprint('main', __name__)
dataset_service = DatasetService()

@main_bp.route('/')
def index():
    """Home page with overview and statistics"""
    return render_template('index.html', title='Big Data Analytics Dashboard')

@main_bp.route('/analysis')
def analysis():
    """Data analysis and processing page"""
    return render_template('analysis.html', title='Data Analysis')

@main_bp.route('/visualizations')
def visualizations():
    """Visualization dashboard page"""
    return render_template('visualizations.html', title='Visualizations')

@main_bp.route('/tracking')
def tracking():
    """Progress tracking page"""
    # Generate sample progress data
    progress_data = {
        'overall_progress': 65.5,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'components': {
            'Data Storage': {
                'progress': 85.0,
                'files': {
                    'storage_service.py': True,
                    'data_connector.py': True,
                    'cache_manager.py': False
                }
            },
            'MapReduce': {
                'progress': 70.0,
                'files': {
                    'mapper.py': True,
                    'reducer.py': True,
                    'job_scheduler.py': False
                }
            },
            'Spark Processing': {
                'progress': 60.0,
                'files': {
                    'spark_service.py': True,
                    'streaming_processor.py': False,
                    'batch_processor.py': True
                }
            },
            'Web Interface': {
                'progress': 75.0,
                'files': {
                    'views.py': True,
                    'services.py': True,
                    'templates/': True
                }
            }
        }
    }
    return render_template('tracking.html', progress_data=progress_data)

@main_bp.route('/tracking/dashboard')
def tracking_dashboard():
    """Project tracking dashboard"""
    # Generate sample progress data for the dashboard
    progress_data = {
        'overall_progress': 68.5,
        'days_until_deadline': 14
    }
    
    # Team progress data
    team_progress = {
        'JH': {
            'individual_development': 85.0,
            'tasks_completed': 8,
            'tasks_total': 10
        },
        'Darrel': {
            'individual_development': 70.0,
            'tasks_completed': 7,
            'tasks_total': 10
        },
        'Xuan Yu': {
            'individual_development': 65.0,
            'tasks_completed': 6,
            'tasks_total': 10
        },
        'Javin': {
            'individual_development': 75.0,
            'tasks_completed': 7,
            'tasks_total': 10
        }
    }
    
    # Integration status
    integration_status = {
        'storage_to_mapreduce': {
            'status': 'completed',
            'message': 'Successfully integrated data storage with MapReduce',
            'last_sync': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        },
        'mapreduce_to_spark': {
            'status': 'in_progress',
            'message': 'Working on connecting MapReduce output to Spark',
            'last_sync': datetime.now().strftime('%Y-%m-%d')
        },
        'spark_to_visualization': {
            'status': 'pending',
            'message': 'Not started yet',
            'last_sync': 'N/A'
        },
        'web_to_visualization': {
            'status': 'in_progress',
            'message': 'Implementing web interface for visualizations',
            'last_sync': datetime.now().strftime('%Y-%m-%d')
        }
    }
    
    # Overdue tasks
    overdue_tasks = [
        {
            'task': 'Implement real-time streaming',
            'phase': 'Individual Development',
            'due_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'progress': 60
        },
        {
            'task': 'Complete MapReduce to Spark integration',
            'phase': 'Integration',
            'due_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'progress': 75
        }
    ]
    
    return render_template('tracking/dashboard.html', 
                          progress_data=progress_data,
                          team_progress=team_progress,
                          integration_status=integration_status,
                          overdue_tasks=overdue_tasks)

@main_bp.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """API endpoint to trigger data analysis"""
    try:
        # Get analysis parameters from request
        params = request.get_json()
        
        # Initialize spark service
        spark_service = SparkService()
        
        # Run analysis with the comprehensive parameters
        result = spark_service.run_analysis(params)
        
        return jsonify({
            "status": "success",
            "message": "Analysis completed successfully",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/stop-analysis', methods=['POST'])
def stop_analysis():
    """API endpoint to stop running analysis"""
    try:
        # Get stop parameters from request
        params = request.get_json()
        
        # Initialize spark service
        spark_service = SparkService()
        
        # Stop the analysis
        spark_service.stop_analysis()
        
        return jsonify({
            "status": "success",
            "message": "Analysis stopped successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/get-visualizations')
def get_visualizations():
    """API endpoint to get visualization data"""
    try:
        # Get visualization parameters from query string
        params = request.args.to_dict()
        
        # Initialize visualization service
        viz_service = VisualizationService()
        
        # Get visualization data
        data = viz_service.get_data(params)
        
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/progress')
def get_progress():
    """API endpoint to get progress data"""
    try:
        # Generate sample progress data
        progress_data = {
            'overall_progress': 65.5,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': {
                'Data Storage': {
                    'progress': 85.0,
                    'files': {
                        'storage_service.py': True,
                        'data_connector.py': True,
                        'cache_manager.py': False
                    }
                },
                'MapReduce': {
                    'progress': 70.0,
                    'files': {
                        'mapper.py': True,
                        'reducer.py': True,
                        'job_scheduler.py': False
                    }
                },
                'Spark Processing': {
                    'progress': 60.0,
                    'files': {
                        'spark_service.py': True,
                        'streaming_processor.py': False,
                        'batch_processor.py': True
                    }
                },
                'Web Interface': {
                    'progress': 75.0,
                    'files': {
                        'views.py': True,
                        'services.py': True,
                        'templates/': True
                    }
                }
            }
        }
        
        return jsonify({
            "status": "success",
            "data": progress_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/progress/update', methods=['POST'])
def update_progress():
    """API endpoint to update project progress"""
    try:
        data = request.get_json()
        
        # In a real application, this would update a database
        # For now, we'll just return success
        
        return jsonify({
            "status": "success",
            "message": "Progress updated successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/integration/update', methods=['POST'])
def update_integration():
    """API endpoint to update integration status"""
    try:
        data = request.get_json()
        
        # In a real application, this would update a database
        # For now, we'll just return success
        
        return jsonify({
            "status": "success",
            "message": "Integration status updated successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/search-datasets')
def search_datasets():
    """API endpoint to search for datasets"""
    try:
        query = request.args.get('query', '')
        source = request.args.get('source', 'all')
        limit = int(request.args.get('limit', 5))
        
        results = dataset_service.search_datasets(query, source, limit)
        
        return jsonify({
            "status": "success",
            "data": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/download-dataset', methods=['POST'])
def download_dataset():
    """API endpoint to download a dataset"""
    try:
        params = request.get_json()
        dataset_id = params.get('dataset_id')
        
        if not dataset_id:
            return jsonify({
                "status": "error",
                "message": "Dataset ID is required"
            })
        
        result = dataset_service.download_dataset(dataset_id)
        
        return jsonify({
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/available-datasets')
def available_datasets():
    """API endpoint to get available datasets"""
    try:
        datasets = dataset_service.get_available_datasets()
        
        return jsonify({
            "status": "success",
            "data": datasets
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/scrape-twitter', methods=['POST'])
def scrape_twitter():
    """API endpoint to scrape Twitter data"""
    try:
        params = request.get_json()
        query = params.get('query')
        limit = int(params.get('limit', 100))
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Query is required"
            })
        
        result = dataset_service.scrape_twitter_data(query, limit)
        
        return jsonify({
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/scrape-reddit', methods=['POST'])
def scrape_reddit():
    """API endpoint to scrape Reddit data"""
    try:
        params = request.get_json()
        subreddit = params.get('subreddit')
        limit = int(params.get('limit', 100))
        
        if not subreddit:
            return jsonify({
                "status": "error",
                "message": "Subreddit is required"
            })
        
        result = dataset_service.scrape_reddit_data(subreddit, limit)
        
        return jsonify({
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@main_bp.route('/api/dataset-file/<path:filename>')
def dataset_file(filename):
    """API endpoint to get a dataset file"""
    try:
        # Ensure the filename is within the data directory
        if '..' in filename or filename.startswith('/'):
            return jsonify({
                "status": "error",
                "message": "Invalid filename"
            })
        
        file_path = os.path.join(dataset_service.data_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "File not found"
            })
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error retrieving file: {str(e)}"
        }) 