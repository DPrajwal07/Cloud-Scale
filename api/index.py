import sys
import os

# Add root directory to sys.path so Vercel can import the main FastAPI app
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from main import app

# Vercel serverless function handlers
handler = app
