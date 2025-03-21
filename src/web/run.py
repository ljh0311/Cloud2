"""
Run the Flask application
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 