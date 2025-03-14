"""
Flask web application for Big Data Analytics Dashboard
"""

from flask import Flask, render_template
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Import blueprints
from src.web.blueprints.tracking import tracking_bp

# Register blueprints
app.register_blueprint(tracking_bp)

@app.route('/')
def index():
    """Home page with overview and statistics"""
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    """Data analysis and processing page"""
    return render_template('analysis.html')

@app.route('/visualizations')
def visualizations():
    """Visualization dashboard page"""
    return render_template('visualizations.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 