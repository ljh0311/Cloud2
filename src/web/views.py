"""
Views for the web application
"""

from flask import Blueprint, render_template, jsonify, request
from .services import SparkService, VisualizationService

main_bp = Blueprint('main', __name__)

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

@main_bp.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """API endpoint to trigger data analysis"""
    try:
        # Get analysis parameters from request
        params = request.get_json()
        
        # Initialize spark service
        spark_service = SparkService()
        
        # Run analysis
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