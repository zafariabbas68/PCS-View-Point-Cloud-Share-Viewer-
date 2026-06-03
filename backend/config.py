import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directories
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_DIR = BASE_DIR / "static" / "models"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions - Stonex formats
ALLOWED_EXTENSIONS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}

# Server settings
HOST = "127.0.0.1"
PORT = 8000

# Maximum file size (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024