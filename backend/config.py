import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# On Render, use /tmp for uploads
if os.environ.get('RENDER'):
    UPLOAD_DIR = Path("/tmp/uploads")
    MODEL_DIR = BASE_DIR / "static" / "models"
else:
    UPLOAD_DIR = BASE_DIR / "uploads"
    MODEL_DIR = BASE_DIR / "static" / "models"

# Create directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Supported formats
ALLOWED_EXTENSIONS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}

# Server settings - IMPORTANT: Use PORT from environment
HOST = "0.0.0.0" if os.environ.get('RENDER') else "127.0.0.1"
PORT = int(os.environ.get('PORT', 10000))  # Render uses PORT env var

MAX_FILE_SIZE = 50 * 1024 * 1024

print(f"Config loaded - RENDER={os.environ.get('RENDER')}")
print(f"PORT={PORT}")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")
print(f"MODEL_DIR: {MODEL_DIR}")