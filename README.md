
# 🌍 PCS-View | Professional Point Cloud Platform

[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-blue?logo=render)](https://pcs-view.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-r128-blue?logo=three.js)](https://threejs.org)
[![Electron](https://img.shields.io/badge/Electron-30.0.0-blue?logo=electron)](https://electronjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **Professional Point Cloud Platform** | Convert, Visualize & Share 3D Point Clouds Instantly

**Live Demo:** [https://pcs-view.onrender.com](https://pcs-view.onrender.com)

---

## 📋 Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Supported Formats](#supported-formats)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Desktop Application](#desktop-application)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Author](#author)
- [License](#license)

---

## 🎯 Overview

**PCS-View** is a professional web-based platform for point cloud visualization, analysis, and sharing. Built for geospatial engineers, surveyors, and Earth observation specialists, it bridges the gap between field data collection and client communication.

### Why PCS-View?

| Problem | Solution |
|---------|----------|
| Clients can't open LAS/E57 files | Browser-based viewer - no software needed |
| Large files are hard to share | Instant conversion to web-friendly formats |
| Expensive cloud subscriptions | Self-hosted, lightweight, and free |
| No measurement tools | Built-in distance measurement and CAD tools |
| CAD workflow integration | Export to multiple formats |
| Need desktop app for offline use | Electron-based native desktop application |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PCS-View Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐         ┌─────────────────────────────────────────┐  │
│   │   Client Side   │         │            Server Side                   │  │
│   │                 │         │                                         │  │
│   │  ┌───────────┐  │  HTTP   │  ┌───────────────────────────────────┐  │  │
│   │  │  Browser  │◄─┼─────────┼──│          FastAPI Server           │  │  │
│   │  │  (Web)    │  │  REST   │  │  (Python 3.12 / Uvicorn)          │  │  │
│   │  └───────────┘  │  API    │  └───────────────────────────────────┘  │  │
│   │                 │         │                   │                     │  │
│   │  ┌───────────┐  │         │  ┌───────────────────────────────────┐  │  │
│   │  │  Electron │  │  IPC    │  │          Backend Modules          │  │  │
│   │  │  Desktop  │◄─┼─────────┼──│  ┌───────────┐  ┌───────────┐  │  │  │
│   │  │  App      │  │         │  │  │ Volume    │  │ Profiles  │  │  │  │
│   │  └───────────┘  │         │  │  │ Calc      │  │ Gen       │  │  │  │
│   │                 │         │  │  └───────────┘  └───────────┘  │  │  │
│   └─────────────────┘         │  │  ┌───────────┐  ┌───────────┐  │  │  │
│                               │  │  │ Road      │  │ Earth     │  │  │  │
│   ┌─────────────────┐         │  │  │ Design    │  │ Works     │  │  │  │
│   │    Frontend      │         │  │  └───────────┘  └───────────┘  │  │  │
│   │    Modules       │         │  │  ┌───────────┐  ┌───────────┐  │  │  │
│   │                  │         │  │  │ CAD Tools │  │ Survey    │  │  │  │
│   │  ┌────────────┐  │         │  │  └───────────┘  └───────────┘  │  │  │
│   │  │ Three.js   │  │         │  └───────────────────────────────────┘  │  │
│   │  │ Viewer     │  │         │                   │                     │  │
│   │  └────────────┘  │         │  ┌───────────────────────────────────┐  │  │
│   │  ┌────────────┐  │         │  │         File System              │  │  │
│   │  │ Glassmorph │  │         │  │  ┌──────────┐  ┌──────────┐    │  │  │
│   │  │ UI Design  │  │         │  │  │ /uploads │  │ /static  │    │  │  │
│   │  └────────────┘  │         │  │  └──────────┘  └──────────┘    │  │  │
│   │  ┌────────────┐  │         │  └───────────────────────────────────┘  │  │
│   │  │ 20+ Tools  │  │         │                                         │  │
│   │  │  Modals    │  │         │   ┌─────────────────────────────────┐   │  │
│   │  └────────────┘  │         │   │    External Services            │   │  │
│   └─────────────────┘         │   │  ┌──────────────────────────┐   │   │  │
│                               │   │  │    Render (Hosting)       │   │   │  │
│                               │   │  └──────────────────────────┘   │   │  │
│                               │   └─────────────────────────────────┘   │  │
│                                                                         │  │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                          DATA FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  User Upload → FastAPI → PLY Conversion → Three.js → 3D Visualization
                                                           ↓
  User Request → API → Backend → Processing → Result → Display
                                                           ↓
  CAD Drawing → Three.js → Scene Update → Display
```

### Architecture Components

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | HTML5, CSS3, JavaScript | Glassmorphism UI with 20+ tool modals |
| **3D Engine** | Three.js + OrbitControls | GPU-accelerated point cloud rendering |
| **Backend** | FastAPI (Python) | RESTful API with 20+ endpoints |
| **Desktop App** | Electron | Cross-platform native application |
| **Processing** | NumPy, SciPy, Matplotlib | Volume calc, profiles, orthophoto |
| **Hosting** | Render (free tier) | Cloud deployment with auto-deploy |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Processing Pipeline                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Upload ──→ Convert ──→ Store ──→ Visualize ──→ Analyze ──→ Export │
│    │          │          │           │            │          │      │
│    ▼          ▼          ▼           ▼            ▼          ▼      │
│  LAS/LAZ    PLY      /static/   Three.js     Volume/     CSV/TXT   │
│  /E57       Format   models/    Rendering    Profiles    /LAS      │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 📤 **Upload & Convert**
- Support for 7+ point cloud formats
- Automatic conversion to web-optimized PLY
- Handles large point clouds efficiently
- Real-time conversion status

### 🖥️ **3D Visualization**
- GPU-accelerated rendering with Three.js
- Smooth orbit controls (rotate, pan, zoom)
- Colored point cloud support (RGB, Elevation, Intensity, Classification)
- Grid and axes helpers for orientation

### 📏 **Professional Tools**

| Tool | Description |
|------|-------------|
| **Volume Calculation** | Convex hull, grid, and TIN methods |
| **Cut & Fill Analysis** | Earthwork volume estimation |
| **Point Classification** | Height-based, ground, vegetation detection |
| **Orthophoto Generation** | Top-view image creation |
| **Profile Generation** | Longitudinal and cross-section profiles |
| **Superelevation** | Road design superelevation calculator |
| **Alignment Creation** | Road alignment design (straight, curve) |
| **Template Designer** | Road template creation (urban, rural, highway) |
| **Esplanade Earthworks** | Elevation-based earthwork calculations |
| **Terrain Analysis** | Slope, aspect, hillshade, contour analysis |
| **Survey Calculation** | Polar, 3D distance, area calculations |
| **Traverse Calculation** | Traverse survey computations |
| **Filtering** | Range, statistical, and voxel filtering |
| **Export** | CSV, TXT, LAS, PLY formats |

### 🎨 **CAD Drawing Tools**
- **Line Tool** - Draw straight lines
- **Circle Tool** - Draw circles
- **Rectangle Tool** - Draw rectangles
- **Arc Tool** - Draw arcs
- **Measure Tool** - Distance measurement between points
- **Clear All** - Remove all CAD drawings

### 🎨 **User Experience**
- Glassmorphism design with backdrop blur
- Drag & drop file upload
- Responsive layout (desktop/tablet/mobile)
- Color-coded results (Cut=Red, Fill=Green)
- Smooth animations and transitions
- Status messages and progress indicators

---

## 📁 Supported Formats

| Format | Extension | Source | Status |
|--------|-----------|--------|--------|
| LAS | `.las` | LiDAR data | ✅ Full |
| LAZ | `.laz` | Compressed LiDAR | ✅ Full |
| E57 | `.e57` | Laser scanners | ✅ Full |
| PLY | `.ply` | Point cloud data | ✅ Full |
| XYZ | `.xyz` | ASCII point cloud | ✅ Full |
| TXT | `.txt` | ASCII point cloud | ✅ Full |
| CX3D | `.cx3d` | Field software | ✅ Full |

---

## 🛠 Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance REST API |
| **Uvicorn** | ASGI server |
| **NumPy** | Numerical operations |
| **SciPy** | Scientific computing (Convex Hull) |
| **Matplotlib** | Orthophoto generation |
| **Laspy** | LAS/LAZ file processing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Three.js** | 3D rendering engine |
| **OrbitControls** | Camera interaction |
| **HTML5/CSS3** | Responsive UI with glassmorphism |
| **Font Awesome** | Icons and visual elements |

### Desktop
| Technology | Purpose |
|------------|---------|
| **Electron** | Cross-platform desktop wrapper |
| **Electron Builder** | Build installers for macOS/Windows/Linux |

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
- Node.js 18+ (for Electron desktop app)
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
pip install -r requirements.txt

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

## 🖥️ Desktop Application

PCS-View is also available as a native desktop application built with Electron.

### Build for macOS

```bash
cd electron
npm install
npm run build:mac
```
Creates: `dist/PCS-View-2.0.0.dmg`

### Build for Windows

```bash
cd electron
npm install
npm run build:win
```
Creates: `dist/PCS-View Setup 2.0.0.exe`

### Build for Linux

```bash
cd electron
npm install
npm run build:linux
```
Creates: `dist/PCS-View-2.0.0.AppImage`

### Build All Platforms

```bash
cd electron
npm run build:all
```

### Desktop Features
- ✅ No Python or Node.js required
- ✅ Native menu bar (File, View, Tools, Help)
- ✅ Keyboard shortcuts (Cmd+I, Cmd+E, etc.)
- ✅ Automatic server startup
- ✅ Works offline
- ✅ File associations for LAS/LAZ/PLY/E57

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage (upload interface) |
| `POST` | `/api/upload` | Upload & convert point cloud |
| `GET` | `/api/projects` | List available models |
| `GET` | `/api/pointcloud/{model}` | Get point cloud data for viewer |
| `GET` | `/api/info/{model}` | Get point cloud metadata |
| `POST` | `/api/volume/{model}` | Calculate volume (convex hull) |
| `POST` | `/api/volume/advanced/{model}` | Advanced volume calculation |
| `POST` | `/api/cutfill/{model}` | Cut & fill analysis |
| `POST` | `/api/classify/height/{model}` | Height-based classification |
| `POST` | `/api/orthophoto/generate/{model}` | Generate orthophoto |
| `POST` | `/api/profile/longitudinal/{model}` | Generate longitudinal profile |
| `POST` | `/api/profile/cross/{model}` | Generate cross section |
| `POST` | `/api/earthworks/esplanade/{model}` | Esplanade earthwork calculation |
| `POST` | `/api/road/superelevation` | Superelevation calculation |
| `POST` | `/api/alignment/create` | Create road alignment |
| `GET` | `/api/export/{model}/{format}` | Export point cloud |

### Example API Call

```bash
# Upload a point cloud
curl -X POST -F "file=@cloud.las" https://pcs-view.onrender.com/api/upload

# Get point cloud info
curl https://pcs-view.onrender.com/api/info/abc123.ply

# Calculate volume
curl -X POST https://pcs-view.onrender.com/api/volume/abc123.ply

# Generate orthophoto
curl -X POST "https://pcs-view.onrender.com/api/orthophoto/generate/abc123.ply?resolution=0.1"

# Export as CSV
curl https://pcs-view.onrender.com/api/export/abc123.ply/csv
```

---

## 📁 Project Structure

```
PCS-View/
│
├── backend/
│   ├── __init__.py          # Package initialization
│   ├── routes.py            # API routes and logic
│   ├── classification.py    # Point cloud classification
│   ├── orthophoto.py        # Orthophoto generation
│   ├── volumes.py           # Volume calculations
│   └── requirements.txt     # Backend dependencies
│
├── frontend/
│   ├── index.html           # Main application
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript modules
│   └── viewer.html          # Viewer page (legacy)
│
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Secure IPC bridge
│   ├── package.json         # Electron dependencies
│   ├── assets/              # Icons and assets
│   └── dist/                # Built installers
│
├── static/
│   ├── models/              # Converted PLY files
│   └── orthophotos/         # Generated orthophotos
│
├── uploads/                 # Temporary upload storage
│
├── Dockerfile               # Container configuration
├── render.yaml              # Render deployment config
├── run.py                   # Launcher script
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
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
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
5. Click "Create Web Service"

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
- Click "Import" or drag & drop
- Supported: LAS, LAZ, E57, PLY, XYZ, TXT, CX3D
- Automatic conversion to PLY format

### 2. 3D Viewer Controls
| Action | Control |
|--------|---------|
| Rotate | Left-click + drag |
| Pan | Right-click + drag |
| Zoom | Scroll wheel |
| Zoom In/Out | Toolbar buttons |
| Reset view | Click "Reset" button |

### 3. Professional Tools
| Tab | Tools |
|-----|-------|
| **Home** | Import, Export, Properties, Volume, Classify, Orthophoto |
| **Clouds** | Load, Info, Filter |
| **Survey** | Calculate, Traverse |
| **Profiles** | Long Profile, Cross Section |
| **Volumes** | Volume, Advanced, Cut & Fill |
| **Road** | Alignment, Superelevation, Template |
| **Earthworks** | Esplanade, Calculate, Terrain |
| **CAD** | Line, Circle, Rectangle, Arc, Clear |

### 4. CAD Drawing
1. Click a CAD tool (Line, Circle, Rectangle, Arc)
2. Click in the 3D view to place points
3. Tool will complete automatically
4. View drawings in the CAD panel

### 5. Measurement
1. Click the "Measure" button (turns red)
2. Click two points in the 3D view
3. Distance appears in the CAD panel

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
  - Land registry and cadastral mapping

### Education
- **MSc Geoinformatics Engineering** - Politecnico di Milano (2023-2025)
  - Thesis: "Land Cover Dynamics and Transitions in Italy: Multi-Temporal Analysis with Global Datasets"
- **Bachelor of Engineering in Geodesy** - Kabul Polytechnic University (2010-2014)

### Technical Skills
```
GIS:     ArcGIS Pro, QGIS, GRASS GIS, ENVI, SNAP, Google Earth Engine
Dev:     Python, FastAPI, Three.js, JavaScript, Docker, HTML/CSS, Electron
Survey:  GNSS, RTK, Total Stations, Drone Photogrammetry, LiDAR
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

- **Politecnico di Milano** - For academic foundation
- **Open3D** - For point cloud processing capabilities
- **Three.js** - For 3D visualization excellence
- **Electron** - For cross-platform desktop support

---

## 📞 Contact & Support

| Channel | Link |
|---------|------|
| **Live Demo** | [pcs-view.onrender.com](https://pcs-view.onrender.com) |
| **GitHub** | [github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-](https://github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-) |
| **Email** | ghalambabas.zafari@gmail.com |
| **Phone** | +39 379 138 7487 |

---

## ⭐ Show Your Support

If this project helped you, please:
- ⭐ Star the repository on GitHub
- 🐙 Follow me for more geospatial projects
- 🔗 Share with your network

---

**Built for Earth Observation and Geospatial Intelligence**

*"From satellites to sovereignty — mapping our shared future"*
