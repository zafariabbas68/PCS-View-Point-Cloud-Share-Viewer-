#!/bin/bash
# Build script for Render

echo "Building PCS-View for Render..."

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create necessary directories
mkdir -p static/models
mkdir -p uploads

echo "Build complete!"
