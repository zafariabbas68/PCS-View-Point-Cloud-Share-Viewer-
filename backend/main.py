
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import shutil
import json
from datetime import datetime
import numpy as np
import logging

from .config import UPLOAD_DIR, MODEL_DIR, ORTHOPHOTO_DIR, PROJECTS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from .converter import convert_point_cloud, calculate_volume, get_point_cloud_info
from .classification import PointCloudClassifier
from .orthophoto import OrthophotoGenerator
from .volumes import VolumeCalculator
from .alignments import AlignmentManager
from .profiles import ProfileGenerator
from .road_design import RoadDesign
from .earthworks import Earthworks
from .survey import SurveyCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PCS-View API", description="Professional Point Cloud Platform")

# Mount static
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================
# PAGE ROUTES
# ============================================

@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    return "<h1>PCS-View</h1>"


# ============================================
# POINT CLOUD OPERATIONS
# ============================================

@app.post("/api/upload")
async def upload_pointcloud(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format")

    unique_id = str(uuid.uuid4())[:8]
    temp_path = UPLOAD_DIR / f"{unique_id}{file_ext}"
    output_path = MODEL_DIR / f"{unique_id}.ply"

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = convert_point_cloud(temp_path, output_path)
        if not result.get("success"):
            raise HTTPException(500, result.get("error", "Conversion failed"))

        return JSONResponse({
            "success": True,
            "model_name": f"{unique_id}.ply",
            "metadata": result,
            "viewer_url": f"/viewer/{unique_id}.ply"
        })
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/pointcloud/{model_name}")
async def get_pointcloud(model_name: str):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    try:
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)
        max_pts = min(len(points), 30000)

        step = max(1, len(points) // max_pts)
        sampled = points[::step][:max_pts]
        colors = np.asarray(pcd.colors)[::step][:max_pts] if pcd.has_colors() else None

        return JSONResponse({
            "points": sampled.tolist(),
            "colors": colors.tolist() if colors is not None else None,
            "count": len(sampled),
            "total_points": len(points)
        })
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/info/{model_name}")
async def get_info(model_name: str):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = get_point_cloud_info(ply_path)
    if "error" in result:
        raise HTTPException(500, result["error"])
    result["file_size_mb"] = round(ply_path.stat().st_size / (1024 * 1024), 2)
    return JSONResponse(result)


# ============================================
# VOLUME OPERATIONS
# ============================================

@app.post("/api/volume/{model_name}")
async def volume_calc(model_name: str):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = calculate_volume(ply_path)
    return JSONResponse(result)


@app.post("/api/volume/advanced/{model_name}")
async def volume_advanced(model_name: str, base_elevation: float = None):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = VolumeCalculator.calculate_volume(ply_path, base_elevation)
    return JSONResponse(result)


@app.post("/api/cutfill/{model_name}")
async def cutfill_analysis(model_name: str):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = VolumeCalculator.cut_fill_analysis(ply_path)
    return JSONResponse(result)


# ============================================
# CLASSIFICATION
# ============================================

@app.post("/api/classify/height/{model_name}")
async def classify_height(model_name: str):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = PointCloudClassifier.classify_by_height(ply_path)
    return JSONResponse(result)


@app.post("/api/classify/ground/{model_name}")
async def classify_ground(model_name: str):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = PointCloudClassifier.ground_classification(ply_path)
    return JSONResponse(result)


# ============================================
# ORTHOPHOTO & CONTOURS
# ============================================

@app.post("/api/orthophoto/generate/{model_name}")
async def generate_ortho(model_name: str, resolution: float = 0.1):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = OrthophotoGenerator.generate_orthophoto(ply_path, resolution)
    if result.get("success"):
        result["orthophoto_url"] = f"/static/orthophotos/{Path(result['orthophoto_path']).name}"
    return JSONResponse(result)


@app.post("/api/contours/generate/{model_name}")
async def generate_contours(model_name: str, interval: float = 1.0):
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")
    result = OrthophotoGenerator.generate_contour_lines(ply_path, interval)
    return JSONResponse(result)


# ============================================
# ALIGNMENTS (NEW)
# ============================================

@app.post("/api/alignment/create")
async def create_alignment(data: dict):
    points = data.get("points", [])
    name = data.get("name", "alignment")
    result = AlignmentManager.create_alignment(points, name)
    return JSONResponse(result)


@app.get("/api/alignment/export/{name}")
async def export_alignment(name: str):
    file_path = PROJECTS_DIR / f"{name}.json"
    if not file_path.exists():
        raise HTTPException(404, "Alignment not found")
    return FileResponse(path=file_path, filename=f"{name}.json")


# ============================================
# PROFILES (NEW)
# ============================================

@app.post("/api/profile/longitudinal/{model_name}")
async def longitudinal_profile(model_name: str):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(pcd.points)
    result = ProfileGenerator.generate_longitudinal_profile(points)
    return JSONResponse(result)


@app.post("/api/profile/cross/{model_name}")
async def cross_profile(model_name: str, center_x: float, center_y: float, width: float = 20.0):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(pcd.points)
    result = ProfileGenerator.generate_cross_section(points, [center_x, center_y], width)
    return JSONResponse(result)


# ============================================
# ROAD DESIGN (NEW)
# ============================================

@app.post("/api/road/superelevation")
async def road_superelevation(speed: float, radius: float):
    result = RoadDesign.calculate_superelevation(speed, radius)
    return JSONResponse(result)


@app.post("/api/road/template")
async def road_template(width: float, lanes: int, shoulder: float = 0.5):
    result = RoadDesign.design_template(width, lanes, shoulder)
    return JSONResponse(result)


# ============================================
# EARTHWORKS (NEW)
# ============================================

@app.post("/api/earthworks/esplanade/{model_name}")
async def esplanade_volume(model_name: str, elevation: float):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(pcd.points)
    result = Earthworks.calculate_volume_by_esplanade(points, elevation)
    return JSONResponse(result)


# ============================================
# EXPORT
# ============================================

@app.get("/api/export/{model_name}/csv")
async def export_csv(model_name: str):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(pcd.points)[:5000]
    lines = ["X,Y,Z"]
    for p in points:
        lines.append(f"{p[0]:.6f},{p[1]:.6f},{p[2]:.6f}")

    return Response(
        content="\n".join(lines),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.csv')}"}
    )


@app.get("/api/export/{model_name}/txt")
async def export_txt(model_name: str):
    import open3d as o3d
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(404, "Model not found")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    points = np.asarray(pcd.points)[:5000]
    lines = [f"# PCS-View Export", f"# Points: {len(points)}", "# X Y Z"]
    for p in points:
        lines.append(f"{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}")

    return Response(
        content="\n".join(lines),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.txt')}"}
    )


# ============================================
# PROJECTS
# ============================================

@app.get("/api/projects")
async def list_projects():
    projects = []
    for f in MODEL_DIR.glob("*.ply"):
        projects.append({
            "name": f.name,
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat()
        })
    return {"projects": projects, "total": len(projects)}


@app.get("/api/formats")
async def get_formats():
    return {"formats": list(ALLOWED_EXTENSIONS)}


@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
