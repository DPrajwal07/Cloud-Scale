import sys
import os

# Ensure root directory and current directory are in sys.path so 'main' can be imported in the Vercel serverless environment
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
current_dir = os.path.dirname(os.path.abspath(__file__))
for path in (root_dir, current_dir, os.getcwd()):
    if path and path not in sys.path:
        sys.path.insert(0, path)

from main import app

# Export for both app and handler runtime conventions
handler = app

