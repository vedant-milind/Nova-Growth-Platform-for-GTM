"""Run the Flask application."""

import os
import sys

# Ensure we're in the flask_app directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n  >>> Open http://127.0.0.1:{port} or http://localhost:{port} in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=port)
