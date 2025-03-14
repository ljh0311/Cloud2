"""
Web application package
"""

from flask import Flask
from flask_bootstrap import Bootstrap5
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    
    # Initialize Flask-Bootstrap
    Bootstrap5(app)
    
    # Import and register blueprints
    from .views import main_bp
    app.register_blueprint(main_bp)
    
    return app 