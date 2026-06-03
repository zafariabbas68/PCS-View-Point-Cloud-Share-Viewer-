import os
import glob
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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
    return """
    <html>
        <body>
            <h1>PCS-View</h1>
            <p>Frontend not found. Please ensure frontend/index.html exists.</p>
        </body>
    </html>
    """


@app.get("/viewer/{model_name}", response_class=HTMLResponse)
async def viewer_page(model_name: str):
    """Serve the 3D viewer page for a specific model."""
    viewer_html_path = Path(__file__).parent.parent / "frontend" / "viewer.html"
    if viewer_html_path.exists():
        html_content = viewer_html_path.read_text()
        html_content = html_content.replace("{{MODEL_NAME}}", model_name)
        return html_content
    return f"""
    <html>
        <body>
            <h1>Viewer</h1>
            <p>Model: {model_name}</p>
            <p>Viewer template not found.</p>
        </body>
    </html>
    """


@app.post("/api/upload")
async def upload_and_convert(file: UploadFile = File(...)):
    """
    Upload a point cloud file, convert to PLY, return the viewer URL.
    Supports Stonex formats: LAS, LAZ, E57, PLY, XYZ, TXT, CX3D
    """
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

        # Verify the output file exists and is readable
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="Conversion produced empty file")

        # Return success response
        viewer_url = f"/viewer/{output_filename}"
        return JSONResponse(content={
            "success": True,
            "viewer_url": viewer_url,
            "model_name": output_filename,
            "metadata": conversion_result,
            "message": f"Successfully converted {file.filename} to viewable format"
        })

    except Exception as e:
        logger.error(f"Upload/conversion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    finally:
        # Clean up temporary upload file
        if temp_input_path.exists():
            temp_input_path.unlink()


@app.get("/api/info/{model_name}")
async def get_pointcloud_metadata(model_name: str):
    """Get detailed metadata about a converted point cloud."""
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
    """Calculate volume for stockpile/earthwork applications."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    result = calculate_volume(ply_path)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return JSONResponse(content=result)


@app.get("/api/export/{model_name}/csv")
async def export_to_csv(model_name: str):
    """Export point cloud to CSV format for Excel/GIS software."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")

    csv_path = MODEL_DIR / f"{model_name.replace('.ply', '.csv')}"

    try:
        import open3d as o3d

        # Read the PLY file
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)

        if len(points) == 0:
            raise HTTPException(status_code=500, detail="No points to export")

        # Write as CSV file
        import csv
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['X', 'Y', 'Z'])
            for point in points:
                writer.writerow([f"{point[0]:.6f}", f"{point[1]:.6f}", f"{point[2]:.6f}"])

        # Verify file was created
        if not csv_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create export file")

        # Return the file
        return FileResponse(
            path=csv_path,
            filename=f"{model_name.replace('.ply', '.csv')}",
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.csv')}"}
        )

    except Exception as e:
        logger.error(f"CSV export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    finally:
        # Clean up the temporary csv file after sending
        if csv_path and csv_path.exists():
            try:
                csv_path.unlink()
            except:
                pass


@app.get("/api/export/{model_name}/txt")
async def export_to_txt(model_name: str):
    """Export point cloud to TXT format (ASCII) for CAD integration."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")

    txt_path = MODEL_DIR / f"{model_name.replace('.ply', '.txt')}"

    try:
        import open3d as o3d

        # Read the PLY file
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)

        if len(points) == 0:
            raise HTTPException(status_code=500, detail="No points to export")

        # Write as XYZ text file
        with open(txt_path, 'w') as f:
            f.write("# PCS-View Exported Point Cloud\n")
            f.write(f"# Source: {model_name}\n")
            f.write(f"# Points: {len(points)}\n")
            f.write("# Format: X Y Z\n")
            for point in points:
                f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f}\n")

        # Verify file was created
        if not txt_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create export file")

        return FileResponse(
            path=txt_path,
            filename=f"{model_name.replace('.ply', '.txt')}",
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={model_name.replace('.ply', '.txt')}"}
        )

    except Exception as e:
        logger.error(f"TXT export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    finally:
        # Clean up the temporary txt file after sending
        if txt_path and txt_path.exists():
            try:
                txt_path.unlink()
            except:
                pass


@app.get("/api/formats")
async def get_supported_formats():
    """Return list of supported file formats."""
    return {
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "stonex_compatible": [".las", ".e57", ".ply", ".xyz", ".cx3d"],
        "description": "Compatible with Stonex X120GO scanner and Cube-3d software",
        "workflow": "Export from Cube-3d → Upload to PCS-View → Share with clients"
    }


@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to check file availability and paths."""
    try:
        static_dir = Path(__file__).parent.parent / "static"
        models_dir = static_dir / "models"

        files = []
        if models_dir.exists():
            files = [f.name for f in models_dir.iterdir() if f.suffix == '.ply']

        config_model_files = []
        if MODEL_DIR.exists():
            config_model_files = [f.name for f in MODEL_DIR.iterdir() if f.suffix == '.ply']

        return {
            "status": "ok",
            "render_env": bool(os.environ.get('RENDER')),
            "current_working_directory": str(Path.cwd()),
            "static_dir_exists": static_dir.exists(),
            "static_dir_path": str(static_dir),
            "models_dir_exists": models_dir.exists(),
            "models_dir_path": str(models_dir),
            "config_model_dir_path": str(MODEL_DIR),
            "config_model_dir_exists": MODEL_DIR.exists(),
            "ply_files_in_static_models": files,
            "ply_files_in_config_models": config_model_files,
            "all_directories": {
                "static": str(static_dir),
                "models": str(models_dir),
                "config_models": str(MODEL_DIR),
                "uploads": str(UPLOAD_DIR)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/debug/file/{filename}")
async def debug_file(filename: str):
    """Check if a specific PLY file exists and is accessible."""
    possible_paths = [
        Path(__file__).parent.parent / "static" / "models" / filename,
        MODEL_DIR / filename,
        Path("/app/static/models") / filename,
    ]

    results = []
    for path in possible_paths:
        results.append({
            "path": str(path),
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None
        })

    return {
        "filename": filename,
        "checks": results,
        "any_exists": any(r["exists"] for r in results)
    }


@app.get("/api/debug/list-all")
async def list_all_files():
    """List all files in static/models directory."""
    try:
        models_dir = Path(__file__).parent.parent / "static" / "models"
        files = []
        if models_dir.exists():
            for f in models_dir.iterdir():
                files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime
                })

        tmp_models = Path("/tmp/static/models") if os.environ.get('RENDER') else None
        tmp_files = []
        if tmp_models and tmp_models.exists():
            for f in tmp_models.iterdir():
                tmp_files.append({
                    "name": f.name,
                    "size": f.stat().st_size
                })

        return {
            "static_models_files": files,
            "tmp_models_files": tmp_files,
            "static_models_path": str(models_dir),
            "models_dir_exists": models_dir.exists(),
            "is_writable": os.access(models_dir, os.W_OK) if models_dir.exists() else False
        }
    except Exception as e:
        return {"error": str(e)}