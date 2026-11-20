

import os
import sys
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/models', exist_ok=True)
os.makedirs('static/orthophotos', exist_ok=True)

app = FastAPI(title="PCS-View API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API routes
app.include_router(router)

# Serve frontend
from fastapi.responses import FileResponse

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/{path:path}")
async def serve_static(path: str):
    file_path = os.path.join("frontend", path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/index.html")

def main():
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("🚀 Starting PCS-View (Professional Point Cloud Platform)")
    print("=" * 50)
    print(f"📡 Server: http://127.0.0.1:{port}")
    print("📁 Upload LAS/LAZ/PLY/XYZ files")
    print("🛠️  All tools available via ribbon tabs")
    print("⏹️  Press CTRL+C to stop")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
