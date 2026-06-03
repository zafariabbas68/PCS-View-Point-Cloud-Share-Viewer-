#!/usr/bin/env python3
"""
Launch script for PCS-View
Run this file to start the server.
"""

import uvicorn
import webbrowser
import threading
import time


def open_browser():
    """Open browser after a short delay."""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting PCS-View (Point Cloud Share Viewer)")
    print("=" * 50)
    print("\n📡 Server will be available at: http://127.0.0.1:8000")
    print("📁 Upload .las or .laz files to convert and view in 3D")
    print("⏹️  Press CTRL+C to stop the server\n")

    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()

    # Start server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)