import os
import json
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, JSONResponse
from scipy.spatial import ConvexHull
import tempfile
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
MODEL_DIR = "static/models"
ORTHOPHOTO_DIR = "static/orthophotos"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(ORTHOPHOTO_DIR, exist_ok=True)

# ===== HELPER FUNCTIONS =====
def load_points(filepath):
    points = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    
    header_end = 0
    for i, line in enumerate(lines):
        if line.strip() == 'end_header':
            header_end = i + 1
            break
    
    for line in lines[header_end:]:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                points.append([float(parts[0]), float(parts[1]), float(parts[2])])
            except:
                pass
    
    return np.array(points) if points else np.array([])

def write_ply(filepath, points, colors=None):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        if colors is not None and len(colors) > 0:
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
        f.write("end_header\n")
        for i, p in enumerate(points):
            if colors is not None and i < len(colors):
                c = colors[i]
                f.write(f"{p[0]} {p[1]} {p[2]} {int(c[0]*255)} {int(c[1]*255)} {int(c[2]*255)}\n")
            else:
                f.write(f"{p[0]} {p[1]} {p[2]}\n")

def sample_points(points, max_points=50000):
    if len(points) <= max_points:
        return points
    indices = np.random.choice(len(points), max_points, replace=False)
    return points[indices]

# ===== API ENDPOINTS =====
@router.get("/api/projects")
async def get_projects():
    models = []
    if os.path.exists(MODEL_DIR):
        for f in os.listdir(MODEL_DIR):
            if f.endswith(('.ply', '.las', '.laz')):
                filepath = os.path.join(MODEL_DIR, f)
                size = os.path.getsize(filepath) / (1024 * 1024)
                models.append({
                    "name": f,
                    "path": filepath,
                    "size_mb": round(size, 2)
                })
    return {"projects": models}

@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename
        ext = filename.split('.')[-1].lower()
        unique_name = f"{os.urandom(4).hex()}.ply"
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{unique_name}")
        output_path = os.path.join(MODEL_DIR, unique_name)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        points = None
        colors = None
        
        if ext in ['las', 'laz']:
            try:
                import laspy
                las = laspy.read(temp_path)
                points = np.vstack([las.x, las.y, las.z]).T
                if hasattr(las, 'red') and las.red is not None:
                    colors = np.vstack([las.red/65535, las.green/65535, las.blue/65535]).T
            except:
                data = np.loadtxt(temp_path)
                points = data[:, :3]
                colors = data[:, 3:6] if data.shape[1] >= 6 else None
        elif ext == 'ply':
            points = load_points(temp_path)
        elif ext in ['xyz', 'txt']:
            data = np.loadtxt(temp_path)
            points = data[:, :3]
            colors = data[:, 3:6] if data.shape[1] >= 6 else None
        else:
            points = load_points(temp_path)
        
        if points is None or len(points) == 0:
            os.remove(temp_path)
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "Could not parse file"}
            )
        
        points = sample_points(points, 50000)
        if colors is not None and len(colors) > len(points):
            colors = colors[:len(points)]
        
        write_ply(output_path, points, colors)
        os.remove(temp_path)
        
        return {
            "success": True,
            "model_name": unique_name,
            "point_count": len(points),
            "message": f"File uploaded and converted to {unique_name}"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": str(e)}
        )

@router.get("/api/pointcloud/{model_name}")
async def get_pointcloud(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Model not found")
    
    points = []
    colors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    
    header_end = 0
    has_colors = False
    for i, line in enumerate(lines):
        if line.strip() == 'end_header':
            header_end = i + 1
            break
        if 'property' in line and 'red' in line:
            has_colors = True
    
    for line in lines[header_end:]:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                points.append([float(parts[0]), float(parts[1]), float(parts[2])])
                if has_colors and len(parts) >= 6:
                    colors.append([float(parts[3])/255, float(parts[4])/255, float(parts[5])/255])
            except:
                pass
    
    if len(points) > 50000:
        indices = np.random.choice(len(points), 50000, replace=False)
        points = [points[i] for i in indices]
        if colors:
            colors = [colors[i] for i in indices]
    
    return {
        "points": points,
        "colors": colors if colors else [],
        "count": len(points),
        "total_points": len(points)
    }

@router.get("/api/info/{model_name}")
async def get_info(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Model not found")
    
    size = os.path.getsize(filepath) / (1024 * 1024)
    points = load_points(filepath)
    
    has_colors = False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'property uchar red' in content:
                has_colors = True
    except:
        pass
    
    return {
        "point_count": len(points),
        "file_size_mb": round(size, 2),
        "has_color": has_colors,
        "has_intensity": False,
        "has_classification": False
    }

@router.post("/api/volume/{model_name}")
async def calculate_volume(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Model not found")
    
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points (need at least 4)"}
    
    try:
        hull = ConvexHull(points)
        return {
            "success": True,
            "volume_cubic_meters": round(hull.volume, 2),
            "area_sqm": round(hull.area, 2)
        }
    except Exception as e:
        return {"success": False, "detail": str(e)}

@router.post("/api/volume/advanced/{model_name}")
async def advanced_volume(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    try:
        hull = ConvexHull(points)
        volume = hull.volume
        area = hull.area
        return {
            "success": True,
            "volume_cubic_meters": round(volume, 2),
            "area_sqm": round(area, 2),
            "avg_height": round(volume / area if area > 0 else 0, 2)
        }
    except Exception as e:
        return {"success": False, "detail": str(e)}

@router.post("/api/cutfill/{model_name}")
async def cutfill(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    mean_z = np.mean(points[:, 2])
    cut = sum(p[2] > mean_z + 0.5 for p in points) * 0.5
    fill = sum(p[2] < mean_z - 0.5 for p in points) * 0.5
    
    return {
        "success": True,
        "cut_volume_cubic_meters": round(cut, 2),
        "fill_volume_cubic_meters": round(fill, 2),
        "net_volume": round(cut - fill, 2)
    }

@router.post("/api/classify/height/{model_name}")
async def classify_height(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    z_vals = points[:, 2]
    ground = np.percentile(z_vals, 10)
    veg = np.percentile(z_vals, 50)
    building = np.percentile(z_vals, 90)
    
    return {
        "success": True,
        "total_points": len(points),
        "ground": int(np.sum(z_vals < ground + 0.5)),
        "vegetation": int(np.sum((z_vals >= ground + 0.5) & (z_vals < building - 0.5))),
        "buildings": int(np.sum(z_vals >= building - 0.5))
    }

@router.post("/api/orthophoto/generate/{model_name}")
async def generate_orthophoto(model_name: str, resolution: float = 0.1):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    ortho_name = f"{model_name.replace('.ply', '')}_ortho.png"
    ortho_path = os.path.join(ORTHOPHOTO_DIR, ortho_name)
    
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        
        x = points[:, 0]
        y = points[:, 1]
        z = points[:, 2]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sc = ax.scatter(x, y, c=z, cmap=cm.viridis, s=1, alpha=0.6)
        ax.set_aspect('equal')
        ax.set_title(f'Orthophoto - {model_name}')
        plt.colorbar(sc, label='Elevation (m)')
        plt.tight_layout()
        plt.savefig(ortho_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return {
            "success": True,
            "orthophoto_url": f"/static/orthophotos/{ortho_name}",
            "resolution": resolution
        }
    except:
        with open(ortho_path.replace('.png', '.txt'), 'w') as f:
            f.write(f"Orthophoto for {model_name}\n")
            f.write(f"Points: {len(points)}\n")
            f.write(f"Resolution: {resolution}\n")
        
        return {
            "success": True,
            "orthophoto_url": f"/static/orthophotos/{ortho_name.replace('.png', '.txt')}",
            "resolution": resolution
        }

@router.post("/api/profile/longitudinal/{model_name}")
async def longitudinal_profile(model_name: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    sorted_idx = np.argsort(points[:, 0])
    sorted_points = points[sorted_idx]
    total_dist = sorted_points[-1, 0] - sorted_points[0, 0]
    
    return {
        "success": True,
        "num_points": len(points),
        "total_distance": round(total_dist, 2),
        "min_elevation": round(np.min(points[:, 2]), 2),
        "max_elevation": round(np.max(points[:, 2]), 2)
    }

@router.post("/api/profile/cross/{model_name}")
async def cross_profile(model_name: str, center_x: float = 0, center_y: float = 0, width: float = 20):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    mask = (np.abs(points[:, 0] - center_x) < width/2) & (np.abs(points[:, 1] - center_y) < width/2)
    filtered = points[mask]
    
    return {
        "success": True,
        "num_points": len(filtered),
        "width": width,
        "min_elevation": round(np.min(filtered[:, 2]) if len(filtered) > 0 else 0, 2),
        "max_elevation": round(np.max(filtered[:, 2]) if len(filtered) > 0 else 0, 2)
    }

@router.post("/api/earthworks/esplanade/{model_name}")
async def esplanade(model_name: str, data: dict = Body(...)):
    filepath = os.path.join(MODEL_DIR, model_name)
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    elevation = data.get('elevation', 0)
    z_vals = points[:, 2]
    
    cut = np.sum(z_vals[z_vals > elevation] - elevation)
    fill = np.sum(elevation - z_vals[z_vals < elevation])
    
    try:
        hull = ConvexHull(points)
        area = hull.area
    except:
        area = 0
    
    return {
        "success": True,
        "cut_volume": round(cut, 2),
        "fill_volume": round(fill, 2),
        "net_volume": round(cut - fill, 2),
        "area_sqm": round(area, 2)
    }

@router.post("/api/road/superelevation")
async def superelevation(data: dict = Body(...)):
    speed = data.get('speed', 80)
    radius = data.get('radius', 100)
    
    e = (speed * speed) / (127 * radius)
    e = min(e, 0.12)
    
    return {
        "success": True,
        "speed": speed,
        "radius": radius,
        "superelevation": round(e * 100, 2)
    }

@router.post("/api/alignment/create")
async def create_alignment(data: dict = Body(...)):
    points = data.get('points', [])
    name = data.get('name', 'alignment1')
    
    return {
        "success": True,
        "name": name,
        "segments": len(points) - 1 if len(points) > 1 else 0
    }

@router.post("/api/contours/generate/{model_name}")
async def generate_contours_api(model_name: str, data: dict = Body(...)):
    """Generate contour lines from point cloud"""
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Model not found")
    
    points = load_points(filepath)
    if len(points) < 4:
        return {"success": False, "detail": "Not enough points"}
    
    interval = data.get('interval', 1.0)
    grid_size = data.get('grid_size', 100)
    smooth = data.get('smooth', 1.0)
    
    try:
        from contours import generate_contours
        
        # Generate contours
        contours = generate_contours(points, interval, grid_size, smooth)
        
        if not contours:
            return {"success": False, "detail": "Could not generate contours"}
        
        # Convert to frontend-friendly format
        contour_data = []
        for contour in contours:
            points_list = []
            for p in contour['points']:
                points_list.append([p['x'], p['y'], p['z']])
            contour_data.append({
                'elevation': contour['elevation'],
                'points': points_list,
                'is_major': contour.get('is_major', False)
            })
        
        return {
            "success": True,
            "contours": contour_data,
            "count": len(contour_data),
            "interval": interval
        }
    except ImportError as e:
        return {"success": False, "detail": f"Import error: {str(e)}"}
    except Exception as e:
        return {"success": False, "detail": str(e)}

@router.get("/api/export/{model_name}/{format}")
async def export_pointcloud(model_name: str, format: str):
    filepath = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Model not found")
    
    points = load_points(filepath)
    
    fd, temp_path = tempfile.mkstemp(suffix=f'.{format}')
    os.close(fd)
    
    if format == 'csv':
        np.savetxt(temp_path, points, delimiter=',', header='x,y,z', comments='')
    elif format == 'pdf':
        with open(temp_path, 'w') as f:
            f.write("PCS-View 3D PDF Export\n")
            f.write(f"Model: {model_name}\n")
            f.write(f"Points: {len(points)}\n")
            f.write("This is a 3D PDF placeholder\n")
    else:
        np.savetxt(temp_path, points, delimiter=' ')
    
    return FileResponse(temp_path, filename=f"{model_name}.{format}")
