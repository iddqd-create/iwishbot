import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# This file is the entry point for Vercel.
# It provides the Flask app instance to the Vercel runtime.
from app.web import app
