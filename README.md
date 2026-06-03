
# 🌍 PCS-View | Professional Point Cloud Platform

[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-blue?logo=render)](https://pcs-view.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-r128-blue?logo=three.js)](https://threejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **Stonex Compatible** | Convert, Visualize & Share 3D Point Clouds Instantly

**Live Demo:** [https://pcs-view.onrender.com](https://pcs-view.onrender.com)

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Supported Formats](#supported-formats)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Author](#author)
- [License](#license)

---

## 🎯 Overview

**PCS-View** is a professional web-based platform for point cloud visualization and sharing. Built for geospatial engineers, surveyors, and Earth observation specialists, it bridges the gap between field data collection and client communication.

### Why PCS-View?

| Problem | Solution |
|---------|----------|
| Clients can't open LAS/E57 files | Browser-based viewer - no software needed |
| Large files are hard to share | Instant conversion to web-friendly PLY |
| Expensive cloud subscriptions | Self-hosted, lightweight, free |
| No measurement tools | Built-in distance measurement |
| CAD workflow integration | Export to TXT format |

---

## ✨ Features

### 📤 **Upload & Convert**
- Support for 7+ point cloud formats
- Automatic conversion to web-optimized PLY
- Handles up to 2 million points
- Real-time conversion status

### 🖥️ **3D Visualization**
- GPU-accelerated rendering with Three.js
- Smooth orbit controls (rotate, pan, zoom)
- Colored point cloud support
- Grid and axes helpers for orientation

### 📏 **Professional Tools**
- **Distance Measurement** - Click two points, get exact distance
- **Volume Calculation** - Stockpile/earthwork volume estimation
- **Point Cloud Metadata** - View point count, bounds, file size
- **Export to TXT** - ASCII format for CAD integration

### 🎨 **User Experience**
- Drag & drop file upload
- Responsive layout (desktop/tablet)

---

## 📁 Supported Formats

| Format | Extension | Stonex Product | Status |
|--------|-----------|----------------|--------|
| LAS | `.las` | X120GO Scanner, Cube-3d | ✅ Full |
| LAZ | `.laz` | Compressed LiDAR | ✅ Full |
| E57 | `.e57` | X120GO Scanner | ✅ Full |
| PLY | `.ply` | X120GO Scanner | ✅ Full |
| XYZ | `.xyz` | Cube-3d export | ✅ Full |
| TXT | `.txt` | ASCII point cloud | ✅ Full |
| CX3D | `.cx3d` | Cube-a field software | ✅ Full |

---

## 🛠 Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance REST API |
| **Open3D** | Point cloud processing & conversion |
| **Uvicorn** | ASGI server |
| **NumPy** | Numerical operations |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Three.js** | 3D rendering engine |
| **PLYLoader** | Point cloud file loading |
| **OrbitControls** | Camera interaction |
| **HTML5/CSS3** | Responsive UI |

### DevOps
| Platform | Purpose |
|----------|---------|
| **Render** | Cloud hosting (free tier) |
| **GitHub** | Version control |
| **Docker** | Containerization (optional) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip package manager
- Git (optional)

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-.git
cd PCS-View-Point-Cloud-Share-Viewer-

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run the application
python run.py

# 5. Open browser
open http://127.0.0.1:8000
```

### Docker Deployment

```bash
# Build image
docker build -t pcs-view .

# Run container
docker run -p 8000:8000 pcs-view
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage (upload interface) |
| `GET` | `/viewer/{model}` | 3D viewer page |
| `POST` | `/api/upload` | Upload & convert point cloud |
| `GET` | `/api/info/{model}` | Get point cloud metadata |
| `POST` | `/api/volume/{model}` | Calculate volume |
| `GET` | `/api/export/{model}/txt` | Export to TXT |
| `GET` | `/api/formats` | List supported formats |
| `GET` | `/api/health` | Health check |

### Example API Call

```bash
# Upload a point cloud
curl -X POST -F "file=@cloud.las" https://pcs-view.onrender.com/api/upload

# Get point cloud info
curl https://pcs-view.onrender.com/api/info/abc123.ply

# Calculate volume
curl -X POST https://pcs-view.onrender.com/api/volume/abc123.ply
```

---

## 📁 Project Structure

```
PCS-View/
│
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── converter.py      # Point cloud conversion logic
│   ├── config.py         # Configuration settings
│   └── requirements.txt  # Python dependencies
│
├── frontend/
│   ├── index.html        # Upload homepage
│   └── viewer.html       # 3D viewer page
│
├── static/
│   └── models/           # Converted PLY files
│
├── uploads/              # Temporary upload storage
│
├── Dockerfile            # Container configuration
├── render.yaml           # Render deployment config
├── run.py                # Launcher script
├── requirements.txt      # Root dependencies
└── README.md             # This file
```

---

## ☁️ Deployment

### Deploy on Render (Free)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use these settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `RENDER = true`
6. Click "Create Web Service"

### Deploy on Railway

```bash
npm install -g @railway/cli
railway login
railway up
```

### Deploy Locally

```bash
python run.py
# Server runs at http://127.0.0.1:8000
```

---

## 🎮 Usage Guide

### 1. Upload a File
- Drag & drop or click to select
- Supported: LAS, LAZ, E57, PLY, XYZ, TXT, CX3D
- Max file size: 100MB (50MB on free tier)

### 2. 3D Viewer Controls
| Action | Control |
|--------|---------|
| Rotate | Left-click + drag |
| Pan | Right-click + drag |
| Zoom | Scroll wheel |
| Reset view | Click "Reset Camera" |

### 3. Professional Tools
| Tool | Function |
|------|----------|
| **Point Cloud Info** | Shows point count, bounds, file size |
| **Calculate Volume** | Estimates stockpile volume in m³ |
| **Export to TXT** | Downloads ASCII point cloud |
| **Measure Distance** | Click two points to measure |
| **Center View** | Resets camera position |

---

## 👨‍💻 Author

**Ghulam Abbas Zafari**
- 🎓 MSc in Geoinformatics Engineering | Politecnico di Milano
- 📍 Milan, Italy
- 📧 ghalambabas.zafari@gmail.com
- 🔗 [LinkedIn](https://linkedin.com/in/ghulam-abbas-zafari-b94105248)

### Professional Experience
- **Cadastral Survey Engineer** (2018-2021)
  - Ministry of Urban Development and Land, Afghanistan
  - High-precision RTK surveys, GNSS, Total Stations

### Education
- **MSc Geoinformatics Engineering** - Politecnico di Milano (2023-2025)
  - Thesis: "Land Cover Dynamics and Transitions in Italy: Multi-Temporal Analysis with Global Datasets"
- **Bachelor of Engineering in Geodesy** - Kabul Polytechnic University (2010-2014)

### Technical Skills
```
GIS:     ArcGIS Pro, QGIS, GRASS GIS, ENVI, SNAP, Google Earth Engine
Dev:     Python, FastAPI, Three.js, JavaScript, Docker
Survey:  GNSS, RTK, Total Stations, Drone Photogrammetry
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Stonex** - For inspiration and format compatibility
- **Politecnico di Milano** - For academic foundation
- **Open3D** - For point cloud processing capabilities
- **Three.js** - For 3D visualization excellence

---

## 📞 Contact & Support

| Channel | Link |
|---------|------|
| **Live Demo** | [pcs-view.onrender.com](https://pcs-view.onrender.com) |
| **GitHub** | [github.com/zafariabbas68](https://github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-) |
| **Email** | ghalambabas.zafari@gmail.com |
| **Phone** | +39 379 138 7487 |

---

## ⭐ Show Your Support

If this project helped you, please:
- ⭐ Star the repository on GitHub
- 🐙 Follow me for more geospatial projects
- 🔗 Share with your network

---

**Built with ❤️ for Earth Observation and Geospatial Intelligence**

*"From satellites to sovereignty — mapping our shared future"*

