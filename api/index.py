import sys
import os

# Add root directory to sys.path so Vercel can import the main FastAPI app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
