import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get('RENDER'):
    UPLOAD_DIR = Path("/tmp/uploads")
    MODEL_DIR = BASE_DIR / "static" / "models"
else:
    UPLOAD_DIR = BASE_DIR / "uploads"
    MODEL_DIR = BASE_DIR / "static" / "models"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".las", ".laz", ".ply", ".e57", ".xyz", ".txt", ".cx3d"}

HOST = "0.0.0.0" if os.environ.get('RENDER') else "127.0.0.1"
PORT = int(os.environ.get('PORT', 10000))

MAX_FILE_SIZE = 50 * 1024 * 1024

print(f"Config loaded - RENDER={os.environ.get('RENDER')}")
print(f"PORT={PORT}")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")
print(f"MODEL_DIR: {MODEL_DIR}")
