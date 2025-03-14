"""
Blueprint for progress tracking functionality
"""
from flask import Blueprint, render_template, jsonify
from ..utils.progress_tracker import ProjectProgressTracker

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/tracking')
def tracking_dashboard():
    """Display the progress tracking dashboard"""
    tracker = ProjectProgressTracker()
    progress_data = tracker.generate_progress_report()
    return render_template('tracking.html', progress_data=progress_data)

@tracking_bp.route('/api/progress')
def get_progress():
    """API endpoint to get current progress data"""
    tracker = ProjectProgressTracker()
    return jsonify(tracker.generate_progress_report()) 