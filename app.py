"""
Main application entry point for the Social Media Analyzer.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from flask import Flask
from flask_cors import CORS
from src.web.views import main_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='src/web/static',
                template_folder='src/web/templates')
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 