# PCS-View - Point Cloud Share Viewer

A lightweight web platform to upload, convert, and visualize 3D point clouds (`.las`/`.laz`) directly in your browser.

## Features

- 📤 Upload LAS/LAZ files
- 🔄 Automatic conversion to web-friendly PLY format
- 🖥️ Interactive 3D viewer with orbit controls
- 📏 Distance measurement tool
- 🔗 Shareable viewer links

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Run the application
python run.py