from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import shutil
from datetime import datetime
import numpy as np

from .config import UPLOAD_DIR, MODEL_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from .converter import convert_point_cloud, calculate_volume, get_point_cloud_info

app = FastAPI(title="PCS-View API", description="Point Cloud Share Viewer - Stonex Compatible")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


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


@app.post("/api/volume/{model_name}")  # Changed to POST
async def compute_volume(model_name: str):
    """Calculate volume for stockpile/earthwork applications."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    result = calculate_volume(ply_path)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return JSONResponse(content=result)


@app.get("/api/export/{model_name}/txt")
async def export_to_txt(model_name: str):
    """Export point cloud to TXT format (ASCII)."""
    ply_path = MODEL_DIR / model_name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    txt_path = MODEL_DIR / f"{model_name.replace('.ply', '.txt')}"

    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(ply_path))
        points = np.asarray(pcd.points)

        # Write as XYZ text file
        with open(txt_path, 'w') as f:
            f.write("# PCS-View Exported Point Cloud\n")
            f.write(f"# Points: {len(points)}\n")
            f.write("# X Y Z\n")
            for point in points:
                f.write(f"{point[0]} {point[1]} {point[2]}\n")

        return FileResponse(
            path=txt_path,
            filename=txt_path.name,
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


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