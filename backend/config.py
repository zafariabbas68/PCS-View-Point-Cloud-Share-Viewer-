import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directories - Use /tmp for Render (writable)
if os.environ.get('RENDER'):
    UPLOAD_DIR = Path("/tmp/uploads")
    MODEL_DIR = Path("/tmp/static/models")
else:
    UPLOAD_DIR = BASE_DIR / "uploads"
    MODEL_DIR = BASE_DIR / "static" / "models"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions - Stonex formats
ALLOWED_EXTENSIONS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}

# Server settings
HOST = "0.0.0.0" if os.environ.get('RENDER') else "127.0.0.1"
PORT = int(os.environ.get('PORT', 8000))

# Maximum file size (50 MB for free tier)
MAX_FILE_SIZE = 50 * 1024 * 1024
