import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import shutil
from datetime import datetime
import numpy as np
import logging

from .config import UPLOAD_DIR, MODEL_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from .converter import convert_point_cloud, calculate_volume, get_point_cloud_info

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PCS-View API", description="Point Cloud Share Viewer - Stonex Compatible")

# Ensure static directory exists
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def upload_page():
    """Serve the upload page."""
    upload_html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if upload_html_path.exists():
        return upload_html_path.read_text()
    return "<h1>PCS-View</h1><p>Frontend not found.</p>"


@app.get("/viewer/{model_name}", response_class=HTMLResponse)
async def viewer_page(model_name: str):
    """Serve the 3D viewer page for a specific model."""
    viewer_html_path = Path(__file__).parent.parent / "frontend" / "viewer.html"
    if viewer_html_path.exists():
        html_content = viewer_html_path.read_text()
        html_content = html_content.replace("{{MODEL_NAME}}", model_name)
        return html_content
    return f"<h1>Model: {model_name}</h1><p>Viewer not found</p>"


@app.post("/api/upload")
async def upload_and_convert(file: UploadFile = File(...)):
    """Upload and convert point cloud file."""
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024 * 1024)} MB")

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate unique filenames
    unique_id = str(uuid.uuid4())[:8]
    temp_input_path = UPLOAD_DIR / f"{unique_id}{file_ext}"
    output_filename = f"{unique_id}.ply"
    output_path = MODEL_DIR / output_filename

    try:
        # Save uploaded file
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert to PLY
        conversion_result = convert_point_cloud(temp_input_path, output_path)

        if not conversion_result.get("success"):
            raise HTTPException(status_code=500, detail=conversion_result.get("error", "Conversion failed"))

        viewer_url = f"/viewer/{output_filename}"
        return JSONResponse(content={
            "success": True,
            "viewer_url": viewer_url,
            "model_name": output_filename,
            "metadata": conversion_result,
            "message": f"Successfully converted {file.filename}"
        })

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    finally:
        if temp_input_path.exists():
            temp_input_path.unlink()


@app.get("/api/info/{model_name}")
async def get_pointcloud_metadata(model_name: str):
    """Get metadata about a converted point cloud."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    result = get_point_cloud_info(ply_path)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    result["file_name"] = model_name
    result["file_size_mb"] = round(ply_path.stat().st_size / (1024 * 1024), 2)
    return JSONResponse(content=result)


@app.post("/api/volume/{model_name}")
async def compute_volume(model_name: str):
    """Calculate volume for stockpile applications."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    result = calculate_volume(ply_path)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return JSONResponse(content=result)


@app.get("/api/export/{model_name}/csv")
async def export_to_csv(model_name: str):
    """Export point cloud to CSV format."""
    ply_path = MODEL_DIR / model_name
    logger.info(f"CSV Export: {ply_path}")

    if not ply_path.exists():
        logger.error(f"File not found: {model_name}")
        raise HTTPException(status_code=404, detail=f"Model not found")

    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)

        logger.info(f"Exporting {len(points)} points to CSV")

        # Limit to 5000 points for performance
        max_points = min(len(points), 5000)
        csv_lines = ["X,Y,Z"]
        for i in range(max_points):
            csv_lines.append(f"{points[i][0]:.6f},{points[i][1]:.6f},{points[i][2]:.6f}")

        content = "\n".join(csv_lines)

        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.csv')}"}
        )

    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/api/export/{model_name}/txt")
async def export_to_txt(model_name: str):
    """Export point cloud to TXT format."""
    ply_path = MODEL_DIR / model_name
    logger.info(f"TXT Export: {ply_path}")

    if not ply_path.exists():
        logger.error(f"File not found: {model_name}")
        raise HTTPException(status_code=404, detail=f"Model not found")

    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)

        logger.info(f"Exporting {len(points)} points to TXT")

        # Limit to 5000 points for performance
        max_points = min(len(points), 5000)
        txt_lines = [f"# PCS-View Export", f"# Points: {max_points}", "# X Y Z"]
        for i in range(max_points):
            txt_lines.append(f"{points[i][0]:.6f} {points[i][1]:.6f} {points[i][2]:.6f}")

        content = "\n".join(txt_lines)

        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.txt')}"}
        )

    except Exception as e:
        logger.error(f"TXT export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/api/formats")
async def get_supported_formats():
    """Return list of supported file formats."""
    return {
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "stonex_compatible": [".las", ".e57", ".ply", ".xyz", ".cx3d"],
        "description": "Compatible with Stonex X120GO scanner and Cube-3d software"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/debug")
async def debug_info():
    """Debug endpoint."""
    try:
        models_dir = Path(__file__).parent.parent / "static" / "models"
        files = []
        if models_dir.exists():
            for f in models_dir.iterdir():
                if f.suffix == '.ply':
                    files.append({"name": f.name, "size": f.stat().st_size})
        return {"status": "ok", "ply_files": files, "count": len(files)}
    except Exception as e:
        return {"status": "error", "message": str(e)}