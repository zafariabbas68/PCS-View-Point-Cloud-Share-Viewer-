import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# On Render, use /tmp for uploads (writable)
# But models must be in a directory that's served statically
if os.environ.get('RENDER'):
    # Uploads go to /tmp (writable)
    UPLOAD_DIR = Path("/tmp/uploads")
    # Models go to a location that FastAPI can serve
    # Create a static directory inside the app
    STATIC_DIR = BASE_DIR / "static"
    MODEL_DIR = STATIC_DIR / "models"
else:
    UPLOAD_DIR = BASE_DIR / "uploads"
    MODEL_DIR = BASE_DIR / "static" / "models"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Also ensure the static directory exists
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions - Stonex formats
ALLOWED_EXTENSIONS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}

# Server settings
HOST = "0.0.0.0" if os.environ.get('RENDER') else "127.0.0.1"
PORT = int(os.environ.get('PORT', 8000))

# Maximum file size (50 MB for free tier)
MAX_FILE_SIZE = 50 * 1024 * 1024

print(f"Config loaded - RENDER={os.environ.get('RENDER')}")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")
print(f"MODEL_DIR: {MODEL_DIR}")
print(f"MODEL_DIR exists: {MODEL_DIR.exists()}")
