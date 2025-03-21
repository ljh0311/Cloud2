"""
LEGACY Flask web application for Big Data Analytics Dashboard
This file is no longer used. The main application entry point is now app.py in the project root.
"""

from flask import Flask, render_template, send_from_directory
import os
from flask_cors import CORS
from .routes.api import api

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config['SECRET_KEY'] = os.urandom(24)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    return app

# Create the Flask application instance
app = create_app()

@app.route('/')
def index():
    """Home page with overview and statistics"""
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    """Data analysis and processing page"""
    return render_template('analysis.html')

@app.route('/datasets')
def datasets():
    return render_template('datasets.html')

# Route to serve dataset files directly
@app.route('/data/<path:filename>')
def serve_dataset(filename):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(app.root_path)), 'data')
    return send_from_directory(data_dir, filename)

@app.route('/visualizations')
def visualizations():
    """Visualization dashboard page"""
    return render_template('visualizations.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 